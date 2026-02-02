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
from datetime import date

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
    HousekeepingDashboardSerializer,
    TaskAssignmentSerializer
)
from api.permissions import IsAdminOrManager


# ===== Housekeeping Tasks =====

class HousekeepingTaskListCreateView(generics.ListCreateAPIView):
    """List all tasks or create new task."""
    permission_classes = [IsAuthenticated]
    serializer_class = HousekeepingTaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'task_type', 'assigned_to', 'room']
    search_fields = ['room__number', 'description', 'notes']
    ordering_fields = ['scheduled_date', 'priority', 'created_at']
    ordering = ['priority', 'scheduled_date']
    
    def get_queryset(self):
        queryset = HousekeepingTask.objects.filter(
            room__property=self.request.user.property
        ).select_related('room', 'assigned_to', 'created_by', 'completed_by')
        
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
    permission_classes = [IsAuthenticated]
    serializer_class = HousekeepingTaskSerializer
    
    def get_queryset(self):
        return HousekeepingTask.objects.filter(
            room__property=self.request.user.property
        ).select_related('room', 'assigned_to', 'created_by', 'completed_by')


class TodayTasksView(generics.ListAPIView):
    """List today's tasks."""
    permission_classes = [IsAuthenticated]
    serializer_class = HousekeepingTaskSerializer
    
    def get_queryset(self):
        today = date.today()
        return HousekeepingTask.objects.filter(
            room__property=self.request.user.property,
            scheduled_date=today
        ).select_related('room', 'assigned_to').order_by('priority', 'room__number')


class MyTasksView(generics.ListAPIView):
    """List tasks assigned to current user."""
    permission_classes = [IsAuthenticated]
    serializer_class = HousekeepingTaskSerializer
    
    def get_queryset(self):
        return HousekeepingTask.objects.filter(
            assigned_to=self.request.user,
            status__in=['PENDING', 'IN_PROGRESS']
        ).select_related('room').order_by('priority', 'scheduled_date')


class StartTaskView(APIView):
    """Mark task as started."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            task = HousekeepingTask.objects.get(
                pk=pk,
                room__property=request.user.property
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
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            task = HousekeepingTask.objects.get(
                pk=pk,
                room__property=request.user.property
            )
            
            if task.status == 'COMPLETED':
                return Response(
                    {'error': 'Task already completed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            task.status = 'COMPLETED'
            task.completed_at = timezone.now()
            task.completed_by = request.user
            
            # Calculate duration if started
            if task.started_at:
                duration = (task.completed_at - task.started_at).total_seconds() / 60
                task.duration_minutes = int(duration)
            
            # Update room status
            if task.task_type == 'CLEANING':
                if task.inspection_required:
                    task.room.status = 'INSPECTING'
                else:
                    task.room.status = 'CLEAN'
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
            property=request.user.property
        )
        
        assigned_to = User.objects.get(id=data['assigned_to'])
        
        created_tasks = []
        for room in rooms:
            task = HousekeepingTask.objects.create(
                room=room,
                task_type=data['task_type'],
                assigned_to=assigned_to,
                scheduled_date=data['scheduled_date'],
                priority=data['priority'],
                description=data.get('description', ''),
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
    permission_classes = [IsAuthenticated]
    serializer_class = RoomInspectionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['room', 'inspector', 'passed', 'requires_rework']
    ordering_fields = ['inspection_date', 'cleanliness_rating']
    ordering = ['-inspection_date']
    
    def get_queryset(self):
        queryset = RoomInspection.objects.filter(
            room__property=self.request.user.property
        ).select_related('room', 'inspector', 'task')
        
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
    permission_classes = [IsAuthenticated]
    serializer_class = RoomInspectionSerializer
    
    def get_queryset(self):
        return RoomInspection.objects.filter(
            room__property=self.request.user.property
        ).select_related('room', 'inspector', 'task')


class InspectionsByRoomView(generics.ListAPIView):
    """Get inspection history for a specific room."""
    permission_classes = [IsAuthenticated]
    serializer_class = RoomInspectionSerializer
    
    def get_queryset(self):
        room_id = self.kwargs.get('room_id')
        return RoomInspection.objects.filter(
            room_id=room_id,
            room__property=self.request.user.property
        ).select_related('room', 'inspector').order_by('-inspection_date')


# ===== Linen Inventory =====

class LinenInventoryListCreateView(generics.ListCreateAPIView):
    """List all linen inventory or create new item."""
    permission_classes = [IsAuthenticated]
    serializer_class = LinenInventorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['item_type']
    search_fields = ['item_name']
    ordering_fields = ['item_name', 'total_quantity', 'last_counted_at']
    ordering = ['item_type', 'item_name']
    
    def get_queryset(self):
        return LinenInventory.objects.filter(
            property=self.request.user.property
        )
    
    def perform_create(self, serializer):
        serializer.save(property=self.request.user.property)


class LinenInventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete linen inventory."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = LinenInventorySerializer
    
    def get_queryset(self):
        return LinenInventory.objects.filter(
            property=self.request.user.property
        )


class LowLinenStockView(generics.ListAPIView):
    """List linen items below minimum quantity."""
    permission_classes = [IsAuthenticated]
    serializer_class = LinenInventorySerializer
    
    def get_queryset(self):
        return LinenInventory.objects.filter(
            property=self.request.user.property
        ).filter(
            total_quantity__lte=models.F('minimum_quantity')
        )


# ===== Amenity Inventory =====

class AmenityInventoryListCreateView(generics.ListCreateAPIView):
    """List all amenity inventory or create new item."""
    permission_classes = [IsAuthenticated]
    serializer_class = AmenityInventorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['item_type']
    search_fields = ['item_name', 'supplier']
    ordering_fields = ['item_name', 'current_stock', 'last_restocked_at']
    ordering = ['item_type', 'item_name']
    
    def get_queryset(self):
        return AmenityInventory.objects.filter(
            property=self.request.user.property
        )
    
    def perform_create(self, serializer):
        serializer.save(property=self.request.user.property)


class AmenityInventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete amenity inventory."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = AmenityInventorySerializer
    
    def get_queryset(self):
        return AmenityInventory.objects.filter(
            property=self.request.user.property
        )


class LowAmenityStockView(generics.ListAPIView):
    """List amenity items that need reordering."""
    permission_classes = [IsAuthenticated]
    serializer_class = AmenityInventorySerializer
    
    def get_queryset(self):
        from django.db import models
        return AmenityInventory.objects.filter(
            property=self.request.user.property,
            current_stock__lte=models.F('minimum_stock')
        ).order_by('current_stock')


# ===== Housekeeping Schedules =====

class HousekeepingScheduleListCreateView(generics.ListCreateAPIView):
    """List all schedules or create new schedule."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = HousekeepingScheduleSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['staff', 'shift_type', 'is_active']
    ordering_fields = ['shift_date', 'shift_start']
    ordering = ['shift_date', 'shift_start']
    
    def get_queryset(self):
        queryset = HousekeepingSchedule.objects.filter(
            staff__property=self.request.user.property
        ).select_related('staff')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(shift_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(shift_date__lte=end_date)
        
        return queryset


class HousekeepingScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a schedule."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = HousekeepingScheduleSerializer
    
    def get_queryset(self):
        return HousekeepingSchedule.objects.filter(
            staff__property=self.request.user.property
        ).select_related('staff')


# ===== Stock Movements =====

class StockMovementListCreateView(generics.ListCreateAPIView):
    """List all stock movements or create new movement."""
    permission_classes = [IsAuthenticated]
    serializer_class = StockMovementSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['item_type', 'movement_type', 'performed_by']
    ordering_fields = ['movement_date', 'created_at']
    ordering = ['-movement_date']
    
    def get_queryset(self):
        queryset = StockMovement.objects.filter(
            property=self.request.user.property
        ).select_related('performed_by')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(movement_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(movement_date__lte=end_date)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(
            property=self.request.user.property,
            performed_by=self.request.user
        )


class StockMovementDetailView(generics.RetrieveAPIView):
    """Retrieve a stock movement."""
    permission_classes = [IsAuthenticated]
    serializer_class = StockMovementSerializer
    
    def get_queryset(self):
        return StockMovement.objects.filter(
            property=self.request.user.property
        ).select_related('performed_by')


# ===== Dashboard & Stats =====

class HousekeepingDashboardView(APIView):
    """Get housekeeping dashboard statistics."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.db import models
        today = date.today()
        property_obj = request.user.property
        
        # Task statistics
        task_stats = HousekeepingTask.objects.filter(
            room__property=property_obj
        ).aggregate(
            pending=Count('id', filter=Q(status='PENDING', scheduled_date=today)),
            in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
            completed_today=Count('id', filter=Q(status='COMPLETED', completed_at__date=today))
        )
        
        # Inspection statistics
        inspection_stats = RoomInspection.objects.filter(
            room__property=property_obj
        ).aggregate(
            today=Count('id', filter=Q(inspection_date=today)),
            failed=Count('id', filter=Q(inspection_date=today, passed=False))
        )
        
        # Room status statistics
        room_stats = Room.objects.filter(
            property=property_obj
        ).aggregate(
            clean=Count('id', filter=Q(status='CLEAN')),
            dirty=Count('id', filter=Q(status='DIRTY')),
            inspecting=Count('id', filter=Q(status='INSPECTING')),
            out_of_order=Count('id', filter=Q(status='OUT_OF_ORDER'))
        )
        
        # Low stock items
        low_stock = AmenityInventory.objects.filter(
            property=property_obj,
            current_stock__lte=models.F('minimum_stock')
        ).count()
        
        data = {
            'pending_tasks': task_stats['pending'] or 0,
            'in_progress_tasks': task_stats['in_progress'] or 0,
            'completed_today': task_stats['completed_today'] or 0,
            'inspections_today': inspection_stats['today'] or 0,
            'failed_inspections': inspection_stats['failed'] or 0,
            'clean_rooms': room_stats['clean'] or 0,
            'dirty_rooms': room_stats['dirty'] or 0,
            'inspecting_rooms': room_stats['inspecting'] or 0,
            'out_of_order_rooms': room_stats['out_of_order'] or 0,
            'low_stock_items': low_stock
        }
        
        serializer = HousekeepingDashboardSerializer(data)
        return Response(serializer.data)
