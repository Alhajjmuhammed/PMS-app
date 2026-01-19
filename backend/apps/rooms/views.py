from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import RoomType, Room, RoomAmenity, RoomBlock, RoomStatusLog
from .forms import RoomTypeForm, RoomForm, RoomBlockForm, RoomStatusForm


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_manager


class RoomTypeListView(LoginRequiredMixin, ListView):
    model = RoomType
    template_name = 'rooms/room_type_list.html'
    context_object_name = 'room_types'
    
    def get_queryset(self):
        queryset = RoomType.objects.all()
        if self.request.user.property:
            queryset = queryset.filter(property=self.request.user.property)
        return queryset


class RoomTypeDetailView(LoginRequiredMixin, DetailView):
    model = RoomType
    template_name = 'rooms/room_type_detail.html'
    context_object_name = 'room_type'


class RoomTypeCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = RoomType
    form_class = RoomTypeForm
    template_name = 'rooms/room_type_form.html'
    success_url = reverse_lazy('rooms:room_type_list')
    
    def form_valid(self, form):
        if self.request.user.property:
            form.instance.property = self.request.user.property
        messages.success(self.request, 'Room type created successfully.')
        return super().form_valid(form)


class RoomTypeUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = RoomType
    form_class = RoomTypeForm
    template_name = 'rooms/room_type_form.html'
    success_url = reverse_lazy('rooms:room_type_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Room type updated successfully.')
        return super().form_valid(form)


class RoomListView(LoginRequiredMixin, ListView):
    model = Room
    template_name = 'rooms/room_list.html'
    context_object_name = 'rooms'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Room.objects.select_related('room_type', 'property').all()
        if self.request.user.property:
            queryset = queryset.filter(property=self.request.user.property)
        
        # Filters
        room_type = self.request.GET.get('room_type')
        if room_type:
            queryset = queryset.filter(room_type_id=room_type)
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        fo_status = self.request.GET.get('fo_status')
        if fo_status:
            queryset = queryset.filter(fo_status=fo_status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room_types'] = RoomType.objects.filter(is_active=True)
        context['status_choices'] = Room.RoomStatus.choices
        context['fo_status_choices'] = Room.FrontOfficeStatus.choices
        return context


class RoomDetailView(LoginRequiredMixin, DetailView):
    model = Room
    template_name = 'rooms/room_detail.html'
    context_object_name = 'room'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_logs'] = self.object.status_logs.all()[:20]
        context['blocks'] = self.object.blocks.all()[:10]
        return context


class RoomCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'rooms/room_form.html'
    success_url = reverse_lazy('rooms:room_list')
    
    def form_valid(self, form):
        if self.request.user.property:
            form.instance.property = self.request.user.property
        messages.success(self.request, 'Room created successfully.')
        return super().form_valid(form)


class RoomUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'rooms/room_form.html'
    success_url = reverse_lazy('rooms:room_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Room updated successfully.')
        return super().form_valid(form)


class RoomStatusUpdateView(LoginRequiredMixin, View):
    """Update room status (AJAX)."""
    
    def post(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        form = RoomStatusForm(request.POST, instance=room)
        
        if form.is_valid():
            old_status = room.status
            new_status = form.cleaned_data['status']
            
            # Log status change
            if old_status != new_status:
                RoomStatusLog.objects.create(
                    room=room,
                    previous_status=old_status,
                    new_status=new_status,
                    changed_by=request.user,
                    notes=form.cleaned_data.get('notes', '')
                )
            
            form.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'status': new_status})
            
            messages.success(request, 'Room status updated.')
            return redirect('rooms:room_detail', pk=pk)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors})
        
        messages.error(request, 'Error updating room status.')
        return redirect('rooms:room_detail', pk=pk)


class RoomBlockListView(LoginRequiredMixin, ListView):
    model = RoomBlock
    template_name = 'rooms/room_block_list.html'
    context_object_name = 'blocks'
    paginate_by = 20


class RoomBlockCreateView(LoginRequiredMixin, CreateView):
    model = RoomBlock
    form_class = RoomBlockForm
    template_name = 'rooms/room_block_form.html'
    success_url = reverse_lazy('rooms:room_block_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Room block created successfully.')
        return super().form_valid(form)


class RoomGridView(LoginRequiredMixin, View):
    """Visual grid view of rooms."""
    template_name = 'rooms/room_grid.html'
    
    def get(self, request):
        rooms = Room.objects.select_related('room_type').filter(is_active=True)
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
            'status_colors': {
                'VC': 'success',
                'VD': 'warning',
                'OC': 'primary',
                'OD': 'info',
                'OOO': 'danger',
                'OOS': 'secondary',
            }
        }
        return render(request, self.template_name, context)


class RoomAmenityListView(LoginRequiredMixin, ListView):
    model = RoomAmenity
    template_name = 'rooms/amenity_list.html'
    context_object_name = 'amenities'
