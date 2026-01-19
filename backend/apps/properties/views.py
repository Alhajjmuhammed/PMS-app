from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Property, Building, Floor, Department
from .forms import PropertyForm, BuildingForm, DepartmentForm


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires admin role."""
    
    def test_func(self):
        return self.request.user.is_manager


class PropertyListView(LoginRequiredMixin, ListView):
    """List all properties."""
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    paginate_by = 20


class PropertyDetailView(LoginRequiredMixin, DetailView):
    """View property details."""
    model = Property
    template_name = 'properties/property_detail.html'
    context_object_name = 'property'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['buildings'] = self.object.buildings.all()
        context['departments'] = self.object.departments.all()
        context['amenities'] = self.object.amenities.all()
        return context


class PropertyCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create new property."""
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    success_url = reverse_lazy('properties:property_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Property created successfully.')
        return super().form_valid(form)


class PropertyUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update property."""
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    
    def get_success_url(self):
        return reverse_lazy('properties:property_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Property updated successfully.')
        return super().form_valid(form)


class PropertyDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete property."""
    model = Property
    template_name = 'properties/property_confirm_delete.html'
    success_url = reverse_lazy('properties:property_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Property deleted successfully.')
        return super().delete(request, *args, **kwargs)


class BuildingListView(LoginRequiredMixin, ListView):
    """List buildings for a property."""
    model = Building
    template_name = 'properties/building_list.html'
    context_object_name = 'buildings'
    
    def get_queryset(self):
        self.property = get_object_or_404(Property, pk=self.kwargs['property_pk'])
        return Building.objects.filter(property=self.property)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['property'] = self.property
        return context


class BuildingCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create new building."""
    model = Building
    form_class = BuildingForm
    template_name = 'properties/building_form.html'
    
    def get_initial(self):
        self.property = get_object_or_404(Property, pk=self.kwargs['property_pk'])
        return {'property': self.property}
    
    def form_valid(self, form):
        form.instance.property = self.property
        messages.success(self.request, 'Building created successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('properties:building_list', kwargs={'property_pk': self.kwargs['property_pk']})


class DepartmentListView(LoginRequiredMixin, ListView):
    """List departments for a property."""
    model = Department
    template_name = 'properties/department_list.html'
    context_object_name = 'departments'
    
    def get_queryset(self):
        self.property = get_object_or_404(Property, pk=self.kwargs['property_pk'])
        return Department.objects.filter(property=self.property)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['property'] = self.property
        return context


class DepartmentCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create new department."""
    model = Department
    form_class = DepartmentForm
    template_name = 'properties/department_form.html'
    
    def get_initial(self):
        self.property = get_object_or_404(Property, pk=self.kwargs['property_pk'])
        return {'property': self.property}
    
    def form_valid(self, form):
        form.instance.property = self.property
        messages.success(self.request, 'Department created successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('properties:department_list', kwargs={'property_pk': self.kwargs['property_pk']})
