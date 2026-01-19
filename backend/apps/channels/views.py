from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView
from django.utils import timezone
from .models import (
    Channel, PropertyChannel, RoomTypeMapping, RatePlanMapping,
    AvailabilityUpdate, RateUpdate, ChannelReservation
)


class ChannelDashboardView(LoginRequiredMixin, View):
    template_name = 'channels/dashboard.html'
    
    def get(self, request):
        connections = PropertyChannel.objects.filter(is_active=True)
        if request.user.property:
            connections = connections.filter(property=request.user.property)
        
        pending_reservations = ChannelReservation.objects.filter(
            status=ChannelReservation.Status.RECEIVED
        ).count()
        
        failed_updates = AvailabilityUpdate.objects.filter(
            status=AvailabilityUpdate.Status.FAILED
        ).count() + RateUpdate.objects.filter(
            status=RateUpdate.Status.FAILED
        ).count()
        
        context = {
            'connections': connections,
            'pending_reservations': pending_reservations,
            'failed_updates': failed_updates,
        }
        return render(request, self.template_name, context)


class ChannelListView(LoginRequiredMixin, ListView):
    model = Channel
    template_name = 'channels/channel_list.html'
    context_object_name = 'channels'


class ChannelDetailView(LoginRequiredMixin, DetailView):
    model = Channel
    template_name = 'channels/channel_detail.html'
    context_object_name = 'channel'


class ConnectionListView(LoginRequiredMixin, ListView):
    model = PropertyChannel
    template_name = 'channels/connection_list.html'
    context_object_name = 'connections'
    
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.property:
            qs = qs.filter(property=self.request.user.property)
        return qs


class ConnectionDetailView(LoginRequiredMixin, DetailView):
    model = PropertyChannel
    template_name = 'channels/connection_detail.html'
    context_object_name = 'connection'


class SyncChannelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        connection = get_object_or_404(PropertyChannel, pk=pk)
        
        # Trigger sync (stub for actual implementation)
        connection.last_sync = timezone.now()
        connection.save()
        
        messages.success(request, f'Sync initiated for {connection.channel.name}')
        return redirect('channels:connection_detail', pk=pk)


class ChannelReservationListView(LoginRequiredMixin, ListView):
    model = ChannelReservation
    template_name = 'channels/reservation_list.html'
    context_object_name = 'reservations'
    paginate_by = 30
    
    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs


class UpdateLogView(LoginRequiredMixin, View):
    template_name = 'channels/update_log.html'
    
    def get(self, request):
        availability_updates = AvailabilityUpdate.objects.all()[:50]
        rate_updates = RateUpdate.objects.all()[:50]
        
        context = {
            'availability_updates': availability_updates,
            'rate_updates': rate_updates,
        }
        return render(request, self.template_name, context)
