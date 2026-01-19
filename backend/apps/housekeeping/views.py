from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from datetime import date
from apps.rooms.models import Room
from .models import HousekeepingTask, RoomInspection, LinenInventory, AmenityInventory, HousekeepingSchedule
from .forms import HousekeepingTaskForm, RoomInspectionForm


class HousekeepingDashboardView(LoginRequiredMixin, View):
    template_name = 'housekeeping/dashboard.html'
    
    def get(self, request):
        today = date.today()
        
        # Task statistics
        tasks = HousekeepingTask.objects.filter(scheduled_date=today)
        if request.user.property:
            tasks = tasks.filter(room__property=request.user.property)
        
        stats = {
            'total': tasks.count(),
            'pending': tasks.filter(status=HousekeepingTask.Status.PENDING).count(),
            'in_progress': tasks.filter(status=HousekeepingTask.Status.IN_PROGRESS).count(),
            'completed': tasks.filter(status=HousekeepingTask.Status.COMPLETED).count(),
        }
        
        # Room status summary
        rooms = Room.objects.filter(is_active=True)
        if request.user.property:
            rooms = rooms.filter(property=request.user.property)
        
        room_stats = {
            'vacant_clean': rooms.filter(status=Room.RoomStatus.VACANT_CLEAN).count(),
            'vacant_dirty': rooms.filter(status=Room.RoomStatus.VACANT_DIRTY).count(),
            'occupied_clean': rooms.filter(status=Room.RoomStatus.OCCUPIED_CLEAN).count(),
            'occupied_dirty': rooms.filter(status=Room.RoomStatus.OCCUPIED_DIRTY).count(),
            'out_of_order': rooms.filter(status=Room.RoomStatus.OUT_OF_ORDER).count(),
        }
        
        # My tasks (for housekeeping staff)
        my_tasks = tasks.filter(assigned_to=request.user)
        
        context = {
            'stats': stats,
            'room_stats': room_stats,
            'my_tasks': my_tasks,
            'today': today,
        }
        return render(request, self.template_name, context)


class TaskListView(LoginRequiredMixin, ListView):
    model = HousekeepingTask
    template_name = 'housekeeping/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = HousekeepingTask.objects.select_related('room', 'assigned_to').all()
        if self.request.user.property:
            queryset = queryset.filter(room__property=self.request.user.property)
        
        # Filters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        date_filter = self.request.GET.get('date')
        if date_filter:
            queryset = queryset.filter(scheduled_date=date_filter)
        else:
            queryset = queryset.filter(scheduled_date=date.today())
        
        return queryset


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = HousekeepingTask
    template_name = 'housekeeping/task_detail.html'
    context_object_name = 'task'


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = HousekeepingTask
    form_class = HousekeepingTaskForm
    template_name = 'housekeeping/task_form.html'
    success_url = reverse_lazy('housekeeping:task_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Task created successfully.')
        return super().form_valid(form)


class TaskStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(HousekeepingTask, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(HousekeepingTask.Status.choices):
            task.status = new_status
            
            if new_status == HousekeepingTask.Status.IN_PROGRESS:
                task.started_at = timezone.now()
            elif new_status == HousekeepingTask.Status.COMPLETED:
                task.completed_at = timezone.now()
                # Update room status
                task.room.status = Room.RoomStatus.VACANT_CLEAN
                task.room.save()
            
            task.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            messages.success(request, 'Task status updated.')
        
        return redirect('housekeeping:task_list')


class TaskAssignView(LoginRequiredMixin, View):
    def post(self, request, pk):
        from apps.accounts.models import User
        
        task = get_object_or_404(HousekeepingTask, pk=pk)
        user_id = request.POST.get('user_id')
        
        if user_id:
            user = get_object_or_404(User, pk=user_id)
            task.assigned_to = user
            task.assigned_at = timezone.now()
            task.save()
            messages.success(request, f'Task assigned to {user.get_full_name()}.')
        
        return redirect('housekeeping:task_detail', pk=pk)


class RoomStatusBoardView(LoginRequiredMixin, View):
    template_name = 'housekeeping/room_status_board.html'
    
    def get(self, request):
        rooms = Room.objects.select_related('room_type', 'floor').filter(is_active=True)
        if request.user.property:
            rooms = rooms.filter(property=request.user.property)
        
        # Group by floor
        floors = {}
        for room in rooms:
            floor_num = room.floor.number if room.floor else 0
            if floor_num not in floors:
                floors[floor_num] = []
            floors[floor_num].append(room)
        
        context = {
            'floors': dict(sorted(floors.items())),
            'status_choices': Room.RoomStatus.choices,
        }
        return render(request, self.template_name, context)


class RoomStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, room_pk):
        room = get_object_or_404(Room, pk=room_pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(Room.RoomStatus.choices):
            room.status = new_status
            room.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            messages.success(request, f'Room {room.room_number} status updated.')
        
        return redirect('housekeeping:room_status_board')


class InspectionListView(LoginRequiredMixin, ListView):
    model = RoomInspection
    template_name = 'housekeeping/inspection_list.html'
    context_object_name = 'inspections'
    paginate_by = 30


class InspectionCreateView(LoginRequiredMixin, CreateView):
    model = RoomInspection
    form_class = RoomInspectionForm
    template_name = 'housekeeping/inspection_form.html'
    success_url = reverse_lazy('housekeeping:inspection_list')
    
    def form_valid(self, form):
        room = get_object_or_404(Room, pk=self.kwargs['room_pk'])
        form.instance.room = room
        form.instance.inspector = self.request.user
        messages.success(self.request, 'Inspection recorded.')
        return super().form_valid(form)


class LinenInventoryView(LoginRequiredMixin, ListView):
    model = LinenInventory
    template_name = 'housekeeping/linen_inventory.html'
    context_object_name = 'items'


class AmenityInventoryView(LoginRequiredMixin, ListView):
    model = AmenityInventory
    template_name = 'housekeeping/amenity_inventory.html'
    context_object_name = 'items'


class ScheduleView(LoginRequiredMixin, ListView):
    model = HousekeepingSchedule
    template_name = 'housekeeping/schedule.html'
    context_object_name = 'schedules'
    
    def get_queryset(self):
        date_filter = self.request.GET.get('date', date.today())
        return HousekeepingSchedule.objects.filter(date=date_filter).select_related('user', 'assigned_floor')
