from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import MaintenanceRequest, Asset
import uuid


class MaintenanceDashboardView(LoginRequiredMixin, View):
    template_name = 'maintenance/dashboard.html'
    
    def get(self, request):
        requests = MaintenanceRequest.objects.all()
        if request.user.property:
            requests = requests.filter(property=request.user.property)
        
        stats = {
            'pending': requests.filter(status=MaintenanceRequest.Status.PENDING).count(),
            'in_progress': requests.filter(status=MaintenanceRequest.Status.IN_PROGRESS).count(),
            'completed_today': requests.filter(status=MaintenanceRequest.Status.COMPLETED).count(),
            'emergency': requests.filter(priority=MaintenanceRequest.Priority.EMERGENCY, status__in=['PENDING', 'ASSIGNED']).count(),
        }
        
        recent_requests = requests.order_by('-created_at')[:10]
        
        context = {'stats': stats, 'recent_requests': recent_requests}
        return render(request, self.template_name, context)


class RequestListView(LoginRequiredMixin, ListView):
    model = MaintenanceRequest
    template_name = 'maintenance/request_list.html'
    context_object_name = 'requests'
    paginate_by = 20


class RequestDetailView(LoginRequiredMixin, DetailView):
    model = MaintenanceRequest
    template_name = 'maintenance/request_detail.html'
    context_object_name = 'request'


class RequestCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceRequest
    template_name = 'maintenance/request_form.html'
    fields = ['room', 'location', 'request_type', 'priority', 'title', 'description']
    success_url = reverse_lazy('maintenance:request_list')
    
    def form_valid(self, form):
        form.instance.reported_by = self.request.user
        form.instance.property = self.request.user.property
        form.instance.request_number = f"MR-{uuid.uuid4().hex[:8].upper()}"
        messages.success(self.request, 'Maintenance request created.')
        return super().form_valid(form)


class RequestUpdateView(LoginRequiredMixin, UpdateView):
    model = MaintenanceRequest
    template_name = 'maintenance/request_form.html'
    fields = ['status', 'assigned_to', 'priority', 'resolution_notes', 'parts_cost', 'labor_hours']
    
    def get_success_url(self):
        return reverse_lazy('maintenance:request_detail', kwargs={'pk': self.object.pk})


class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'maintenance/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 20


class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = 'maintenance/asset_detail.html'
    context_object_name = 'asset'


class AssetCreateView(LoginRequiredMixin, CreateView):
    model = Asset
    template_name = 'maintenance/asset_form.html'
    fields = ['name', 'code', 'category', 'location', 'room', 'brand', 'model', 'serial_number', 'purchase_date', 'purchase_cost']
    success_url = reverse_lazy('maintenance:asset_list')
    
    def form_valid(self, form):
        form.instance.property = self.request.user.property
        return super().form_valid(form)
