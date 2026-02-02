"""
Views for POS Module
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from datetime import date
from decimal import Decimal

from apps.pos.models import MenuCategory, MenuItem, POSOrder, POSOrderItem, Outlet
from .pos_serializers import (
    MenuCategorySerializer,
    MenuItemSerializer,
    POSOrderSerializer,
    POSOrderItemSerializer,
    POSDashboardSerializer,
    POSOrderCreateSerializer,
    POSOrderUpdateSerializer,
    OutletSerializer
)
from api.permissions import IsAdminOrManager


# ===== Menu Categories =====

class MenuCategoryListCreateView(generics.ListCreateAPIView):
    """List all menu categories or create new category."""
    permission_classes = [IsAuthenticated]
    serializer_class = MenuCategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['outlet', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['sort_order', 'name']
    ordering = ['sort_order']
    
    def get_queryset(self):
        return MenuCategory.objects.filter(
            outlet__property=self.request.user.property
        ).select_related('outlet').prefetch_related('items')


class MenuCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a menu category."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = MenuCategorySerializer
    
    def get_queryset(self):
        return MenuCategory.objects.filter(
            outlet__property=self.request.user.property
        ).select_related('outlet')


# ===== Menu Items =====

class MenuItemListCreateView(generics.ListCreateAPIView):
    """List all menu items or create new item."""
    permission_classes = [IsAuthenticated]
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_available', 'is_taxable']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price']
    ordering = ['name']
    
    def get_queryset(self):
        return MenuItem.objects.filter(
            category__outlet__property=self.request.user.property
        ).select_related('category', 'category__outlet')


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a menu item."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = MenuItemSerializer
    
    def get_queryset(self):
        return MenuItem.objects.filter(
            category__outlet__property=self.request.user.property
        ).select_related('category')


class MenuItemsByCategoryView(generics.ListAPIView):
    """Get menu items by category."""
    permission_classes = [IsAuthenticated]
    serializer_class = MenuItemSerializer
    
    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        return MenuItem.objects.filter(
            category_id=category_id,
            category__outlet__property=self.request.user.property
        )


class AvailableMenuItemsView(generics.ListAPIView):
    """List available menu items."""
    permission_classes = [IsAuthenticated]
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name']
    
    def get_queryset(self):
        return MenuItem.objects.filter(
            category__outlet__property=self.request.user.property,
            is_available=True
        ).select_related('category')


# ===== POS Orders =====

class POSOrderListCreateView(generics.ListCreateAPIView):
    """List all POS orders or create new order."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['outlet', 'status', 'is_posted_to_room']
    search_fields = ['order_number', 'guest_name', 'room_number']
    ordering_fields = ['created_at', 'total']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return POSOrderCreateSerializer
        return POSOrderSerializer
    
    def get_queryset(self):
        queryset = POSOrder.objects.filter(
            outlet__property=self.request.user.property
        ).select_related('outlet', 'server', 'check_in').prefetch_related('items')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # Verify outlet belongs to property
        try:
            outlet = Outlet.objects.get(
                id=data['outlet'],
                property=request.user.property
            )
        except Outlet.DoesNotExist:
            return Response(
                {'error': 'Outlet not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create order
        order = POSOrder.objects.create(
            outlet=outlet,
            check_in_id=data.get('check_in'),
            room_number=data.get('room_number', ''),
            guest_name=data.get('guest_name', ''),
            table_number=data.get('table_number', ''),
            covers=data.get('covers', 1),
            notes=data.get('notes', ''),
            server=request.user
        )
        
        # Create order items and calculate totals
        subtotal = Decimal('0')
        tax_rate = Decimal('0.10')  # 10% tax
        
        for item_data in data['items']:
            menu_item = MenuItem.objects.get(id=item_data['menu_item'])
            quantity = item_data['quantity']
            unit_price = menu_item.price
            
            POSOrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                unit_price=unit_price,
                notes=item_data.get('notes', '')
            )
            
            subtotal += unit_price * quantity
        
        # Calculate tax and total
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        
        order.subtotal = subtotal
        order.tax_amount = tax_amount
        order.total = total
        order.save()
        
        response_serializer = POSOrderSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class POSOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a POS order."""
    permission_classes = [IsAuthenticated]
    serializer_class = POSOrderSerializer
    
    def get_queryset(self):
        return POSOrder.objects.filter(
            outlet__property=self.request.user.property
        ).select_related('outlet', 'server').prefetch_related('items')


class OpenPOSOrdersView(generics.ListAPIView):
    """List open POS orders."""
    permission_classes = [IsAuthenticated]
    serializer_class = POSOrderSerializer
    
    def get_queryset(self):
        return POSOrder.objects.filter(
            outlet__property=self.request.user.property,
            status='OPEN'
        ).select_related('outlet').prefetch_related('items').order_by('-created_at')


class ClosePOSOrderView(APIView):
    """Close a POS order."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            order = POSOrder.objects.get(
                pk=pk,
                outlet__property=request.user.property
            )
            
            if order.status != 'OPEN':
                return Response(
                    {'error': 'Order is not open'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            order.status = 'CLOSED'
            order.save()
            
            serializer = POSOrderSerializer(order)
            return Response(serializer.data)
            
        except POSOrder.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class PostToRoomView(APIView):
    """Post POS order to room."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            order = POSOrder.objects.get(
                pk=pk,
                outlet__property=request.user.property
            )
            
            if order.is_posted_to_room:
                return Response(
                    {'error': 'Order already posted to room'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not order.check_in and not order.room_number:
                return Response(
                    {'error': 'Room information is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # In real implementation, this would create a folio charge
            order.is_posted_to_room = True
            order.posted_at = timezone.now()
            order.status = 'CLOSED'
            order.save()
            
            serializer = POSOrderSerializer(order)
            return Response({
                'message': 'Order posted to room successfully',
                'order': serializer.data
            })
            
        except POSOrder.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )


# ===== POS Order Items =====

class POSOrderItemListView(generics.ListAPIView):
    """List items for a specific order."""
    permission_classes = [IsAuthenticated]
    serializer_class = POSOrderItemSerializer
    
    def get_queryset(self):
        order_id = self.kwargs.get('order_id')
        return POSOrderItem.objects.filter(
            order_id=order_id,
            order__outlet__property=self.request.user.property
        ).select_related('menu_item', 'order')


class POSOrderItemCreateView(generics.CreateAPIView):
    """Add item to an order."""
    permission_classes = [IsAuthenticated]
    serializer_class = POSOrderItemSerializer
    
    def perform_create(self, serializer):
        order_item = serializer.save()
        
        # Recalculate order totals
        order = order_item.order
        items = order.items.filter(is_voided=False)
        
        subtotal = sum(item.amount for item in items)
        tax_rate = Decimal('0.10')
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount - order.discount
        
        order.subtotal = subtotal
        order.tax_amount = tax_amount
        order.total = total
        order.save()


# ===== Outlets =====

class OutletListView(generics.ListAPIView):
    """List all outlets."""
    permission_classes = [IsAuthenticated]
    serializer_class = OutletSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering = ['name']
    
    def get_queryset(self):
        return Outlet.objects.filter(
            property=self.request.user.property,
            is_active=True
        )


# ===== Dashboard & Stats =====

class POSDashboardView(APIView):
    """Get POS dashboard statistics."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        today = date.today()
        property_obj = request.user.property
        
        # Order statistics
        open_orders = POSOrder.objects.filter(
            outlet__property=property_obj,
            status='OPEN'
        ).count()
        
        orders_today = POSOrder.objects.filter(
            outlet__property=property_obj,
            created_at__date=today
        )
        
        stats = orders_today.aggregate(
            count=Count('id'),
            revenue=Sum('total'),
            covers=Sum('covers')
        )
        
        orders_today_count = stats['count'] or 0
        revenue_today = stats['revenue'] or Decimal('0')
        covers_today = stats['covers'] or 0
        
        avg_check_size = Decimal('0')
        if orders_today_count > 0:
            avg_check_size = revenue_today / orders_today_count
        
        # Top selling items today
        top_items = POSOrderItem.objects.filter(
            order__outlet__property=property_obj,
            order__created_at__date=today,
            is_voided=False
        ).values(
            'menu_item__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_amount=Sum('amount')
        ).order_by('-total_quantity')[:5]
        
        top_selling_items = [
            {
                'name': item['menu_item__name'],
                'quantity': item['total_quantity'],
                'amount': float(item['total_amount'])
            }
            for item in top_items
        ]
        
        data = {
            'open_orders': open_orders,
            'orders_today': orders_today_count,
            'revenue_today': revenue_today,
            'covers_today': covers_today,
            'avg_check_size': round(avg_check_size, 2),
            'top_selling_items': top_selling_items
        }
        
        serializer = POSDashboardSerializer(data)
        return Response(serializer.data)
