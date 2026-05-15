"""
Comprehensive Views for Housekeeping Module  
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.db.models import Q, Count
from django.core.exceptions import ValidationError
from django.db import transaction, DatabaseError
from datetime import date
import logging

from apps.housekeeping.models import (
    HousekeepingTask,
    RoomInspection,
    LinenInventory,
    AmenityInventory,
    HousekeepingSchedule,
    StockMovement
)
from apps.rooms.models import Room
from apps.accounts.models import User
from .housekeeping_serializers import (
    HousekeepingTaskSerializer,
    RoomInspectionSerializer,
    LinenInventorySerializer,
    AmenityInventorySerializer,
    HousekeepingScheduleSerializer,
    StockMovementSerializer,
    TaskAssignmentSerializer
)
from api.permissions import IsAdminOrManager, IsHousekeepingStaff

logger = logging.getLogger(__name__)


# ===== Housekeeping Tasks =====

class HousekeepingTaskListCreateView(generics.ListCreateAPIView):
    """List all tasks or create new task."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    serializer_class = HousekeepingTaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'task_type', 'assigned_to', 'room']
    search_fields = ['room__room_number', 'description', 'notes']
    ordering_fields = ['scheduled_date', 'priority', 'created_at']
    ordering = ['priority', 'scheduled_date']
    
    def get_queryset(self):
        queryset = HousekeepingTask.objects.filter(
            room__hotel=self.request.user.assigned_property
        ).select_related('room', 'assigned_to', 'created_by', 'inspected_by')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(scheduled_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(scheduled_date__lte=end_date)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class HousekeepingTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a task."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    serializer_class = HousekeepingTaskSerializer
    
    def get_queryset(self):
        return HousekeepingTask.objects.filter(
            room__hotel=self.request.user.assigned_property
        ).select_related('room', 'assigned_to', 'created_by', 'inspected_by')


class TodayTasksView(generics.ListAPIView):
    """List today's tasks."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    serializer_class = HousekeepingTaskSerializer
    
    def get_queryset(self):
        today = date.today()
        return HousekeepingTask.objects.filter(
            room__hotel=self.request.user.assigned_property,
            scheduled_date=today
        ).select_related('room', 'assigned_to').order_by('priority', 'room__room_number')


class MyTasksView(generics.ListAPIView):
    """List tasks assigned to current user."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    serializer_class = HousekeepingTaskSerializer
    
    def get_queryset(self):
        qs = HousekeepingTask.objects.filter(
            assigned_to=self.request.user,
            status__in=['PENDING', 'IN_PROGRESS']
        )
        # Multi-tenancy: defensive filter by property
        if self.request.user.assigned_property:
            qs = qs.filter(room__hotel=self.request.user.assigned_property)
        return qs.select_related('room').order_by('priority', 'scheduled_date')


class StartTaskView(APIView):
    """Mark task as started."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    
    def post(self, request, pk):
        try:
            task = HousekeepingTask.objects.get(
                pk=pk,
                room__hotel=request.user.assigned_property
            )
            
            if task.status != 'PENDING':
                return Response(
                    {'error': 'Task is not in pending status'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            task.status = 'IN_PROGRESS'
            task.started_at = timezone.now()
            task.save()
            
            serializer = HousekeepingTaskSerializer(task)
            return Response(serializer.data)
            
        except HousekeepingTask.DoesNotExist:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class CompleteTaskView(APIView):
    """Mark task as completed."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]

    @transaction.atomic
    def post(self, request, pk):
        try:
            task = HousekeepingTask.objects.get(
                pk=pk,
                room__hotel=request.user.assigned_property
            )
            
            if task.status == 'COMPLETED':
                return Response(
                    {'error': 'Task already completed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            task.status = 'COMPLETED'
            task.completed_at = timezone.now()

            # Update room status to Clean when a cleaning task completes
            if task.task_type == 'CLEANING':
                if task.room.status == 'VD':
                    task.room.status = 'VC'
                    task.room.save()
                elif task.room.status == 'OD':
                    task.room.status = 'OC'
                    task.room.save()

            task.save()
            
            serializer = HousekeepingTaskSerializer(task)
            return Response(serializer.data)
            
        except HousekeepingTask.DoesNotExist:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class BulkTaskAssignView(APIView):
    """Assign tasks to multiple rooms."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request):
        serializer = TaskAssignmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        rooms = Room.objects.filter(
            id__in=data['rooms'],
            hotel=request.user.assigned_property
        )
        
        try:
            assigned_to = User.objects.get(
                id=data['assigned_to'],
                assigned_property=request.user.assigned_property
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found in your property'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        created_tasks = []
        with transaction.atomic():
            for room in rooms:
                task = HousekeepingTask.objects.create(
                    room=room,
                    task_type=data['task_type'],
                    assigned_to=assigned_to,
                    scheduled_date=data['scheduled_date'],
                    priority=data['priority'],
                    notes=data.get('description', ''),
                    created_by=request.user
                )
                created_tasks.append(task)
        
        response_serializer = HousekeepingTaskSerializer(created_tasks, many=True)
        return Response({
            'message': f'Created {len(created_tasks)} tasks',
            'tasks': response_serializer.data
        }, status=status.HTTP_201_CREATED)


# ===== Room Inspections =====

class RoomInspectionListCreateView(generics.ListCreateAPIView):
    """List all inspections or create new inspection."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    serializer_class = RoomInspectionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['room', 'inspector', 'passed']
    ordering_fields = ['inspection_date']
    ordering = ['-inspection_date']
    
    def get_queryset(self):
        queryset = RoomInspection.objects.filter(
            room__hotel=self.request.user.assigned_property
        ).select_related('room', 'inspector')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(inspection_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(inspection_date__lte=end_date)
        
        return queryset


class RoomInspectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an inspection."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    serializer_class = RoomInspectionSerializer
    
    def get_queryset(self):
        return RoomInspection.objects.filter(
            room__hotel=self.request.user.assigned_property
        ).select_related('room', 'inspector')


class InspectionsByRoomView(generics.ListAPIView):
    """Get inspection history for a specific room."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    serializer_class = RoomInspectionSerializer
    
    def get_queryset(self):
        room_id = self.kwargs.get('room_id')
        return RoomInspection.objects.filter(
            room_id=room_id,
            room__hotel=self.request.user.assigned_property
        ).select_related('room', 'inspector').order_by('-inspection_date')


# ===== Linen Inventory =====

class LinenInventoryListCreateView(generics.ListCreateAPIView):
    """List all linen inventory or create new item."""
    serializer_class = LinenInventorySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminOrManager()]
        return [IsAuthenticated(), IsHousekeepingStaff()]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['linen_type']
    search_fields = ['linen_type']
    ordering_fields = ['linen_type', 'quantity_total']
    ordering = ['linen_type']
    
    def get_queryset(self):
        return LinenInventory.objects.filter(
            hotel=self.request.user.assigned_property
        )
    
    def perform_create(self, serializer):
        serializer.save(hotel=self.request.user.assigned_property)


class LinenInventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete linen inventory."""
    serializer_class = LinenInventorySerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAuthenticated(), IsAdminOrManager()]
        return [IsAuthenticated(), IsHousekeepingStaff()]

    def get_queryset(self):
        return LinenInventory.objects.filter(
            hotel=self.request.user.assigned_property
        )


class LowLinenStockView(generics.ListAPIView):
    """List linen items below reorder level."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    serializer_class = LinenInventorySerializer
    
    def get_queryset(self):
        from django.db.models import F
        return LinenInventory.objects.filter(
            hotel=self.request.user.assigned_property,
            quantity_total__lte=F('reorder_level')
        )


# ===== Amenity Inventory =====

class AmenityInventoryListCreateView(generics.ListCreateAPIView):
    """List all amenity inventory or create new item."""
    serializer_class = AmenityInventorySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminOrManager()]
        return [IsAuthenticated(), IsHousekeepingStaff()]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'quantity']
    ordering = ['name']
    
    def get_queryset(self):
        return AmenityInventory.objects.filter(
            hotel=self.request.user.assigned_property
        )
    
    def perform_create(self, serializer):
        serializer.save(hotel=self.request.user.assigned_property)


class AmenityInventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete amenity inventory."""
    serializer_class = AmenityInventorySerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAuthenticated(), IsAdminOrManager()]
        return [IsAuthenticated(), IsHousekeepingStaff()]

    def get_queryset(self):
        return AmenityInventory.objects.filter(
            hotel=self.request.user.assigned_property
        )


class LowAmenityStockView(generics.ListAPIView):
    """List amenity items that need reordering."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    serializer_class = AmenityInventorySerializer
    
    def get_queryset(self):
        from django.db.models import F
        return AmenityInventory.objects.filter(
            hotel=self.request.user.assigned_property,
            quantity__lte=F('reorder_level')
        ).order_by('quantity')


# ===== Housekeeping Schedules =====

class HousekeepingScheduleListCreateView(generics.ListCreateAPIView):
    """List all schedules or create new schedule."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = HousekeepingScheduleSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'assigned_floor']
    ordering_fields = ['date', 'shift_start']
    ordering = ['date', 'shift_start']
    
    def get_queryset(self):
        queryset = HousekeepingSchedule.objects.filter(
            user__assigned_property=self.request.user.assigned_property
        ).select_related('user')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset


class HousekeepingScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a schedule."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = HousekeepingScheduleSerializer
    
    def get_queryset(self):
        return HousekeepingSchedule.objects.filter(
            user__assigned_property=self.request.user.assigned_property
        ).select_related('user')


# ===== Stock Movements =====

class StockMovementListCreateView(generics.ListCreateAPIView):
    """List all stock movements or create new movement."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    serializer_class = StockMovementSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['movement_type', 'created_by']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = StockMovement.objects.filter(
            property=self.request.user.assigned_property
        ).select_related('created_by', 'amenity_inventory', 'linen_inventory')

        # Housekeeping staff only see movements they personally created
        if self.request.user.role == 'HOUSEKEEPING':
            queryset = queryset.filter(created_by=self.request.user)

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset
    
    @transaction.atomic
    def perform_create(self, serializer):
        movement_type = serializer.validated_data.get('movement_type')
        # User always submits a positive number; we store it signed so the log
        # is self-describing: +N = stock increased, -N = stock decreased.
        abs_qty = abs(serializer.validated_data.get('quantity', 0))
        REDUCES_STOCK = ('ISSUE', 'DAMAGE')
        signed_qty = -abs_qty if movement_type in REDUCES_STOCK else abs_qty

        amenity_inv = serializer.validated_data.get('amenity_inventory')
        linen_inv = serializer.validated_data.get('linen_inventory')

        if amenity_inv:
            if movement_type in ('RECEIVE', 'RETURN'):
                amenity_inv.quantity += abs_qty
            elif movement_type in REDUCES_STOCK:
                amenity_inv.quantity = max(0, amenity_inv.quantity - abs_qty)
            elif movement_type == 'ADJUST':
                amenity_inv.quantity = abs_qty
            # TRANSFER: quantity unchanged
            amenity_inv.save(update_fields=['quantity'])
            balance_after = amenity_inv.quantity

        elif linen_inv:
            if movement_type == 'RECEIVE':
                linen_inv.quantity_total += abs_qty
            elif movement_type == 'ISSUE':
                linen_inv.quantity_in_use = min(
                    linen_inv.quantity_in_use + abs_qty,
                    linen_inv.quantity_total,
                )
            elif movement_type == 'RETURN':
                linen_inv.quantity_in_use = max(0, linen_inv.quantity_in_use - abs_qty)
            elif movement_type == 'DAMAGE':
                linen_inv.quantity_damaged = min(
                    linen_inv.quantity_damaged + abs_qty,
                    linen_inv.quantity_total,
                )
            elif movement_type == 'ADJUST':
                linen_inv.quantity_total = abs_qty
            # TRANSFER: no change
            linen_inv.save(update_fields=[
                'quantity_total', 'quantity_in_use',
                'quantity_in_laundry', 'quantity_damaged',
            ])
            balance_after = (
                linen_inv.quantity_total
                - linen_inv.quantity_in_use
                - linen_inv.quantity_in_laundry
                - linen_inv.quantity_damaged
            )
        else:
            balance_after = 0
            signed_qty = 0

        serializer.save(
            property=self.request.user.assigned_property,
            created_by=self.request.user,
            quantity=signed_qty,          # overwrite with signed value
            balance_after=max(0, balance_after),
        )


class StockMovementDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete a stock movement."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    serializer_class = StockMovementSerializer

    def get_queryset(self):
        return StockMovement.objects.filter(
            property=self.request.user.assigned_property
        ).select_related('created_by', 'amenity_inventory', 'linen_inventory')

    def destroy(self, request, *args, **kwargs):
        """Delete a movement. Only ADMIN/MANAGER can delete."""
        if request.user.role not in ('ADMIN', 'MANAGER'):
            return Response(
                {'detail': 'Only managers can delete stock movements.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


# ===== Dashboard & Stats =====

class HousekeepingDashboardView(APIView):
    """Get housekeeping dashboard statistics."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    
    def get(self, request):
        today = date.today()
        property_obj = request.user.assigned_property
        
        # Simplified dashboard data with safe defaults
        data = {
            'pending_tasks': 0,
            'in_progress_tasks': 0,
            'completed_today': 0,
            'inspections_today': 0,
            'failed_inspections': 0,
            'clean_rooms': 24,
            'dirty_rooms': 0,
            'inspecting_rooms': 0,
            'out_of_order_rooms': 0,
            'low_stock_items': 0
        }
        
        # For HOUSEKEEPING role: scope to rooms/tasks assigned to this user only.
        # For ADMIN/MANAGER accessing this endpoint: show full property scope.
        is_hk_role = getattr(request.user, 'role', None) == 'HOUSEKEEPING'

        try:
            if property_obj:
                if is_hk_role:
                    # Only rooms assigned to this user via HousekeepingTask
                    assigned_room_ids = HousekeepingTask.objects.filter(
                        assigned_to=request.user
                    ).values_list('room_id', flat=True).distinct()
                    room_qs = Room.objects.filter(
                        id__in=assigned_room_ids, hotel=property_obj, is_active=True
                    )
                else:
                    room_qs = Room.objects.filter(hotel=property_obj, is_active=True)

                total_rooms = room_qs.count()
                room_stats = room_qs.aggregate(
                    clean=Count('id', filter=Q(status__in=('VC', 'OC'))),
                    dirty=Count('id', filter=Q(status__in=('VD', 'OD'))),
                    inspecting=Count('id', filter=Q(status='INSPECTING')),
                    out_of_order=Count('id', filter=Q(status__in=('OOO', 'OOS')))
                )
                data.update({
                    'total_rooms': total_rooms,
                    'clean_rooms': room_stats.get('clean', 0),
                    'dirty_rooms': room_stats.get('dirty', 0),
                    'inspecting_rooms': room_stats.get('inspecting', 0),
                    'out_of_order_rooms': room_stats.get('out_of_order', 0),
                })
        except (DatabaseError, ValidationError, AttributeError) as e:
            logger.warning(f"Failed to fetch room statistics: {str(e)}")

        # Tasks: scope to assigned user for HOUSEKEEPING, full property otherwise
        try:
            if property_obj:
                if is_hk_role:
                    task_qs = HousekeepingTask.objects.filter(
                        assigned_to=request.user, room__hotel=property_obj
                    )
                else:
                    task_qs = HousekeepingTask.objects.filter(room__hotel=property_obj)
                data['pending_tasks'] = task_qs.filter(status='PENDING').count()
                data['in_progress_tasks'] = task_qs.filter(status='IN_PROGRESS').count()
                data['completed_today'] = task_qs.filter(
                    status='COMPLETED', completed_at__date=today
                ).count()
        except (DatabaseError, AttributeError):
            pass

        return Response(data)


# ===== Choices =====

class HousekeepingChoicesView(APIView):
    """Return all enum choices for housekeeping module dynamically."""
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]

    def get(self, request):
        return Response({
            'task_types': [
                {'value': v, 'label': l}
                for v, l in HousekeepingTask.TaskType.choices
            ],
            'priorities': [
                {'value': v, 'label': l}
                for v, l in HousekeepingTask.Priority.choices
            ],
            'statuses': [
                {'value': v, 'label': l}
                for v, l in HousekeepingTask.Status.choices
            ],
            'movement_types': [
                {'value': v, 'label': l}
                for v, l in StockMovement.MovementType.choices
            ],
            'linen_types': [
                {'value': v, 'label': l}
                for v, l in LinenInventory.LinenType.choices
            ],
        })
