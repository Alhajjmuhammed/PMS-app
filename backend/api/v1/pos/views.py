from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.pos.models import Outlet, MenuCategory, MenuItem, POSOrder, POSOrderItem
from apps.billing.models import Folio, FolioCharge, ChargeCode
from apps.frontdesk.models import CheckIn
from api.permissions import IsPOSStaff
from .serializers import (
    OutletSerializer, MenuCategorySerializer, MenuItemSerializer,
    POSOrderSerializer, OrderCreateSerializer, AddOrderItemSerializer
)


class OutletListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsPOSStaff]
    serializer_class = OutletSerializer
    
    def get_queryset(self):
        qs = Outlet.objects.filter(is_active=True)
        if self.request.user.assigned_property:
            qs = qs.filter(property=self.request.user.assigned_property)
        return qs


class OutletDetailView(generics.RetrieveAPIView):
    """Get POS outlet details."""
    permission_classes = [IsAuthenticated, IsPOSStaff]
    serializer_class = OutletSerializer
    queryset = Outlet.objects.filter(is_active=True)


class MenuView(APIView):
    permission_classes = [IsAuthenticated, IsPOSStaff]
    
    def get(self, request, pk):
        try:
            outlet = Outlet.objects.get(pk=pk)
        except Outlet.DoesNotExist:
            return Response({'error': 'Outlet not found'}, status=status.HTTP_404_NOT_FOUND)
        
        categories = MenuCategory.objects.filter(
            outlet=outlet,
            is_active=True
        ).prefetch_related('items')
        
        return Response({
            'outlet': OutletSerializer(outlet).data,
            'categories': MenuCategorySerializer(categories, many=True).data
        })


class OrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsPOSStaff]
    serializer_class = POSOrderSerializer
    
    def get_queryset(self):
        qs = POSOrder.objects.select_related('outlet').prefetch_related('items')
        
        if self.request.user.assigned_property:
            qs = qs.filter(outlet__property=self.request.user.assigned_property)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        
        outlet = self.request.query_params.get('outlet')
        if outlet:
            qs = qs.filter(outlet_id=outlet)
        
        return qs.order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsPOSStaff]
    serializer_class = POSOrderSerializer
    queryset = POSOrder.objects.all()


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated, IsPOSStaff]
    
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            outlet = Outlet.objects.get(pk=data['outlet_id'])
        except Outlet.DoesNotExist:
            return Response({'error': 'Outlet not found'}, status=status.HTTP_404_NOT_FOUND)
        
        order = POSOrder.objects.create(
            outlet=outlet,
            room_number=data.get('room_number', ''),
            guest_name=data.get('guest_name', ''),
            table_number=data.get('table_number', ''),
            covers=data.get('covers', 1),
            server=request.user
        )
        
        return Response(POSOrderSerializer(order).data, status=status.HTTP_201_CREATED)


class AddItemView(APIView):
    permission_classes = [IsAuthenticated, IsPOSStaff]
    
    def post(self, request, pk):
        try:
            order = POSOrder.objects.get(pk=pk)
        except POSOrder.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if order.status != 'OPEN':
            return Response({'error': 'Order is not open'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = AddOrderItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            menu_item = MenuItem.objects.get(pk=data['menu_item_id'])
        except MenuItem.DoesNotExist:
            return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        POSOrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=data.get('quantity', 1),
            unit_price=menu_item.price,
            notes=data.get('notes', '')
        )
        
        # Recalculate totals
        items = order.items.filter(is_voided=False)
        order.subtotal = sum(item.amount for item in items)
        order.tax_amount = order.subtotal * 0.1  # 10% tax
        order.total = order.subtotal + order.tax_amount - order.discount
        order.save()
        
        return Response(POSOrderSerializer(order).data)


class PostToRoomView(APIView):
    permission_classes = [IsAuthenticated, IsPOSStaff]
    
    def post(self, request, pk):
        try:
            order = POSOrder.objects.get(pk=pk)
        except POSOrder.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not order.room_number:
            return Response({'error': 'No room number specified'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find guest check-in
        check_in = CheckIn.objects.filter(
            room__room_number=order.room_number,
            check_out__isnull=True
        ).first()
        
        if not check_in:
            return Response({'error': 'No active check-in found for room'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find folio
        folio = Folio.objects.filter(reservation=check_in.reservation).first()
        if not folio:
            return Response({'error': 'No folio found'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get F&B charge code
        charge_code = ChargeCode.objects.filter(category='FOOD').first()
        if not charge_code:
            charge_code = ChargeCode.objects.create(
                code='FB',
                name='Food & Beverage',
                category='FOOD'
            )
        
        # Create folio charge
        FolioCharge.objects.create(
            folio=folio,
            charge_code=charge_code,
            description=f'POS: {order.outlet.name} - {order.order_number}',
            quantity=1,
            unit_price=order.total,
            posted_by=request.user
        )
        
        # Update order
        order.is_posted_to_room = True
        order.posted_at = timezone.now()
        order.check_in = check_in
        order.status = 'CLOSED'
        order.save()
        
        # Recalculate folio
        folio.recalculate_totals()
        
        return Response({'message': 'Posted to room successfully'})


class MenuCategoryListView(generics.ListCreateAPIView):
    """List and create menu categories."""
    permission_classes = [IsAuthenticated, IsPOSStaff]
    serializer_class = MenuCategorySerializer
    
    def get_queryset(self):
        outlet_id = self.kwargs.get('outlet_id')
        return MenuCategory.objects.filter(outlet_id=outlet_id, is_active=True)
    
    def perform_create(self, serializer):
        outlet_id = self.kwargs.get('outlet_id')
        outlet = get_object_or_404(Outlet, pk=outlet_id)
        serializer.save(outlet=outlet)


class MenuCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a menu category."""
    permission_classes = [IsAuthenticated, IsPOSStaff]
    serializer_class = MenuCategorySerializer
    queryset = MenuCategory.objects.all()


class MenuItemListView(generics.ListCreateAPIView):
    """List and create menu items."""
    permission_classes = [IsAuthenticated, IsPOSStaff]
    serializer_class = MenuItemSerializer
    
    def get_queryset(self):
        qs = MenuItem.objects.select_related('category__outlet')
        
        # Filter by outlet if specified
        outlet_id = self.request.query_params.get('outlet')
        if outlet_id:
            qs = qs.filter(category__outlet_id=outlet_id)
        
        # Filter by category if specified
        category_id = self.request.query_params.get('category')
        if category_id:
            qs = qs.filter(category_id=category_id)
        
        return qs


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a menu item."""
    permission_classes = [IsAuthenticated, IsPOSStaff]
    serializer_class = MenuItemSerializer
    queryset = MenuItem.objects.all()
