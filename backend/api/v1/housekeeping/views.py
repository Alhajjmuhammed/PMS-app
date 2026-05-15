from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from datetime import date
from apps.housekeeping.models import (
    HousekeepingTask, AmenityInventory, LinenInventory,
    StockMovement
)
from apps.rooms.models import Room
from api.permissions import IsHousekeepingStaff
from .serializers import (
    HousekeepingTaskSerializer, TaskUpdateSerializer,
    AmenityInventorySerializer, AmenityInventoryCreateSerializer,
    LinenInventorySerializer, LinenInventoryCreateSerializer,
    StockMovementSerializer, StockMovementCreateSerializer
)


class TaskListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    serializer_class = HousekeepingTaskSerializer
    
    def get_queryset(self):
        qs = HousekeepingTask.objects.select_related('room', 'assigned_to')
        
        if self.request.user.assigned_property:
            qs = qs.filter(room__hotel=self.request.user.assigned_property)
        
        # Filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        
        date_filter = self.request.query_params.get('date')
        if date_filter:
            qs = qs.filter(scheduled_date=date_filter)
        else:
            qs = qs.filter(scheduled_date=date.today())
        
        floor = self.request.query_params.get('floor')
        if floor:
            qs = qs.filter(room__floor_id=floor)
        
        return qs.order_by('priority', 'room__room_number')


class TaskDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    serializer_class = HousekeepingTaskSerializer
    
    def get_queryset(self):
        qs = HousekeepingTask.objects.all()
        if self.request.user.assigned_property:
            qs = qs.filter(room__hotel=self.request.user.assigned_property)
        return qs
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskUpdateSerializer
        return HousekeepingTaskSerializer


class MyTasksView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    serializer_class = HousekeepingTaskSerializer
    
    def get_queryset(self):
        return HousekeepingTask.objects.filter(
            assigned_to=self.request.user,
            scheduled_date=date.today(),
            status__in=['PENDING', 'IN_PROGRESS']
        ).order_by('priority', 'room__room_number')


class StartTaskView(APIView):
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    
    def post(self, request, pk):
        prop = request.user.assigned_property
        try:
            task_qs = HousekeepingTask.objects.all()
            if prop:
                task_qs = task_qs.filter(room__hotel=prop)
            task = task_qs.get(pk=pk)
        except HousekeepingTask.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if task.status != 'PENDING':
            return Response(
                {'error': 'Task is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = 'IN_PROGRESS'
        task.started_at = timezone.now()
        task.assigned_to = request.user
        task.save()
        
        return Response(HousekeepingTaskSerializer(task).data)


class CompleteTaskView(APIView):
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    
    def post(self, request, pk):
        prop = request.user.assigned_property
        try:
            task_qs = HousekeepingTask.objects.all()
            if prop:
                task_qs = task_qs.filter(room__hotel=prop)
            task = task_qs.get(pk=pk)
        except HousekeepingTask.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TaskUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        task.status = 'COMPLETED'
        task.completed_at = timezone.now()
        
        if 'notes' in serializer.validated_data:
            task.notes = serializer.validated_data['notes']
        
        with transaction.atomic():
            task.save()
            
            # Update room status to clean
            room = task.room
            if room.status == 'VD':
                room.status = 'VC'
            elif room.status == 'OD':
                room.status = 'OC'
            room.save()
        
        return Response(HousekeepingTaskSerializer(task).data)


class RoomStatusView(APIView):
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    
    def get(self, request):
        rooms = Room.objects.filter(is_active=True)
        
        if request.user.assigned_property:
            rooms = rooms.filter(hotel=request.user.assigned_property)
        
        floor = request.query_params.get('floor')
        if floor:
            rooms = rooms.filter(floor_id=floor)
        
        rooms = rooms.select_related('room_type', 'floor')
        room_ids = [r.id for r in rooms]
        
        # Pre-fetch all today's pending/in-progress tasks in one query
        today = date.today()
        tasks_by_room = {}
        for task in HousekeepingTask.objects.filter(
            room_id__in=room_ids,
            scheduled_date=today,
            status__in=['PENDING', 'IN_PROGRESS']
        ):
            tasks_by_room[task.room_id] = task
        
        room_data = []
        for room in rooms:
            pending_task = tasks_by_room.get(room.id)
            room_data.append({
                'id': room.id,
                'room_number': room.room_number,
                'room_type': room.room_type.name,
                'floor': room.floor.name if room.floor else '',
                'status': room.status,
                'fo_status': room.fo_status,
                'has_pending_task': pending_task is not None,
                'task_status': pending_task.status if pending_task else None
            })
        
        return Response({'rooms': room_data})


class UpdateRoomStatusView(APIView):
    """Update room housekeeping status."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    
    def post(self, request, room_id):
        prop = request.user.assigned_property
        try:
            room_qs = Room.objects.all()
            if prop:
                room_qs = room_qs.filter(hotel=prop)
            room = room_qs.get(pk=room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
        
        new_status = request.data.get('status')
        if not new_status:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate status — must match Room.RoomStatus choices (2-3 char codes)
        valid_statuses = ['VC', 'VD', 'OC', 'OD', 'OOO', 'OOS']
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        room.status = new_status
        room.save()
        
        return Response({'message': 'Room status updated', 'status': new_status})


# ============= Inventory Management Views =============

class AmenityInventoryListCreateView(generics.ListCreateAPIView):
    """List all amenity inventory items or create a new one."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['hotel', 'category']
    search_fields = ['name', 'code']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = AmenityInventory.objects.select_related('hotel')
        if self.request.user.assigned_property:
            queryset = queryset.filter(hotel=self.request.user.assigned_property)
        
        # Filter by low stock (annotate to keep it a QuerySet)
        low_stock = self.request.query_params.get('low_stock')
        if low_stock == 'true':
            from django.db.models import F
            queryset = queryset.filter(quantity__lte=F('reorder_level'))
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AmenityInventoryCreateSerializer
        return AmenityInventorySerializer

    def perform_create(self, serializer):
        prop = self.request.user.assigned_property
        if prop:
            serializer.save(hotel=prop)
        else:
            serializer.save()


class AmenityInventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an amenity inventory item."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    
    def get_queryset(self):
        queryset = AmenityInventory.objects.select_related('hotel')
        if self.request.user.assigned_property:
            queryset = queryset.filter(hotel=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AmenityInventoryCreateSerializer
        return AmenityInventorySerializer


class LinenInventoryListCreateView(generics.ListCreateAPIView):
    """List all linen inventory items or create a new one."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['hotel', 'linen_type']
    search_fields = ['linen_type']
    ordering = ['linen_type']
    
    def get_queryset(self):
        queryset = LinenInventory.objects.select_related('hotel')
        if self.request.user.assigned_property:
            queryset = queryset.filter(hotel=self.request.user.assigned_property)
        
        # Filter by low stock (annotate to keep it a QuerySet)
        low_stock = self.request.query_params.get('low_stock')
        if low_stock == 'true':
            from django.db.models import F, ExpressionWrapper, IntegerField
            queryset = queryset.annotate(
                qty_available=ExpressionWrapper(
                    F('quantity_total') - F('quantity_in_use') - F('quantity_in_laundry') - F('quantity_damaged'),
                    output_field=IntegerField()
                )
            ).filter(qty_available__lte=F('reorder_level'))
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LinenInventoryCreateSerializer
        return LinenInventorySerializer

    def perform_create(self, serializer):
        prop = self.request.user.assigned_property
        if prop:
            serializer.save(hotel=prop)
        else:
            serializer.save()


class LinenInventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a linen inventory item."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    
    def get_queryset(self):
        queryset = LinenInventory.objects.select_related('hotel')
        if self.request.user.assigned_property:
            queryset = queryset.filter(hotel=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return LinenInventoryCreateSerializer
        return LinenInventorySerializer


class StockMovementListCreateView(generics.ListCreateAPIView):
    """List all stock movements or create a new one."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['property', 'movement_type', 'amenity_inventory', 'linen_inventory']
    search_fields = ['reference', 'reason']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = StockMovement.objects.select_related(
            'property', 'amenity_inventory', 'linen_inventory', 'created_by'
        )
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StockMovementCreateSerializer
        return StockMovementSerializer


class StockMovementDetailView(generics.RetrieveAPIView):
    """Retrieve a stock movement record."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    serializer_class = StockMovementSerializer
    
    def get_queryset(self):
        queryset = StockMovement.objects.select_related(
            'property', 'amenity_inventory', 'linen_inventory', 'created_by'
        )
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset
