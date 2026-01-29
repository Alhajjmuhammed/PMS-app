from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import date
from apps.housekeeping.models import HousekeepingTask, RoomInspection
from apps.rooms.models import Room
from api.permissions import IsHousekeepingStaff
from .serializers import HousekeepingTaskSerializer, TaskUpdateSerializer


class TaskListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    serializer_class = HousekeepingTaskSerializer
    
    def get_queryset(self):
        qs = HousekeepingTask.objects.select_related('room', 'assigned_to')
        
        if self.request.user.assigned_property:
            qs = qs.filter(room__property=self.request.user.assigned_property)
        
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
    queryset = HousekeepingTask.objects.all()
    
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
        try:
            task = HousekeepingTask.objects.get(pk=pk)
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
        try:
            task = HousekeepingTask.objects.get(pk=pk)
        except HousekeepingTask.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TaskUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        task.status = 'COMPLETED'
        task.completed_at = timezone.now()
        
        if 'notes' in serializer.validated_data:
            task.notes = serializer.validated_data['notes']
        
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
            rooms = rooms.filter(property=request.user.assigned_property)
        
        floor = request.query_params.get('floor')
        if floor:
            rooms = rooms.filter(floor_id=floor)
        
        room_data = []
        for room in rooms.select_related('room_type', 'floor'):
            # Check for pending tasks
            pending_task = HousekeepingTask.objects.filter(
                room=room,
                scheduled_date=date.today(),
                status__in=['PENDING', 'IN_PROGRESS']
            ).first()
            
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
    
    def post(self, request, pk):
        try:
            room = Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
        
        new_status = request.data.get('status')
        if not new_status:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate status
        valid_statuses = ['CLEAN', 'DIRTY', 'INSPECTED', 'OUT_OF_ORDER']
        if new_status not in valid_statuses:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        room.status = new_status
        room.save()
        
        return Response({'message': 'Room status updated', 'status': new_status})
