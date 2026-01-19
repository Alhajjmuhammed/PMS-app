from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q, Count, Sum
from datetime import datetime, timedelta
from .models import Reservation, ReservationRoom, GroupBooking, ReservationLog
from .forms import ReservationForm, ReservationRoomFormSet, GroupBookingForm


class ReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'reservations/reservation_list.html'
    context_object_name = 'reservations'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Reservation.objects.select_related('guest', 'property').all()
        if self.request.user.property:
            queryset = queryset.filter(property=self.request.user.property)
        
        # Filters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(check_in_date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(check_in_date__lte=date_to)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(confirmation_number__icontains=search) |
                Q(guest__first_name__icontains=search) |
                Q(guest__last_name__icontains=search) |
                Q(guest__email__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Reservation.Status.choices
        return context


class ReservationDetailView(LoginRequiredMixin, DetailView):
    model = Reservation
    template_name = 'reservations/reservation_detail.html'
    context_object_name = 'reservation'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rooms'] = self.object.rooms.select_related('room_type', 'room').all()
        context['logs'] = self.object.logs.all()[:20]
        return context


class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservations/reservation_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['room_formset'] = ReservationRoomFormSet(self.request.POST)
        else:
            context['room_formset'] = ReservationRoomFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        room_formset = context['room_formset']
        
        if room_formset.is_valid():
            form.instance.created_by = self.request.user
            if self.request.user.property:
                form.instance.property = self.request.user.property
            
            self.object = form.save()
            room_formset.instance = self.object
            room_formset.save()
            
            # Log creation
            ReservationLog.objects.create(
                reservation=self.object,
                action='Created',
                new_value=f"Status: {self.object.status}",
                user=self.request.user
            )
            
            messages.success(self.request, f'Reservation {self.object.confirmation_number} created successfully.')
            return redirect('reservations:reservation_detail', pk=self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        return reverse_lazy('reservations:reservation_detail', kwargs={'pk': self.object.pk})


class ReservationUpdateView(LoginRequiredMixin, UpdateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservations/reservation_form.html'
    
    def form_valid(self, form):
        form.instance.modified_by = self.request.user
        
        # Log changes
        if form.has_changed():
            changes = ', '.join(form.changed_data)
            ReservationLog.objects.create(
                reservation=self.object,
                action='Updated',
                new_value=f"Changed: {changes}",
                user=self.request.user
            )
        
        messages.success(self.request, 'Reservation updated successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('reservations:reservation_detail', kwargs={'pk': self.object.pk})


class ReservationCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        old_status = reservation.status
        
        reservation.status = Reservation.Status.CANCELLED
        reservation.modified_by = request.user
        reservation.save()
        
        # Log cancellation
        ReservationLog.objects.create(
            reservation=reservation,
            action='Cancelled',
            old_value=f"Status: {old_status}",
            new_value=f"Status: {reservation.status}",
            user=request.user
        )
        
        messages.success(request, f'Reservation {reservation.confirmation_number} cancelled.')
        return redirect('reservations:reservation_detail', pk=pk)


class ReservationConfirmView(LoginRequiredMixin, View):
    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        old_status = reservation.status
        
        reservation.status = Reservation.Status.CONFIRMED
        reservation.modified_by = request.user
        reservation.save()
        
        # Log confirmation
        ReservationLog.objects.create(
            reservation=reservation,
            action='Confirmed',
            old_value=f"Status: {old_status}",
            new_value=f"Status: {reservation.status}",
            user=request.user
        )
        
        messages.success(request, f'Reservation {reservation.confirmation_number} confirmed.')
        return redirect('reservations:reservation_detail', pk=pk)


class ReservationSearchView(LoginRequiredMixin, View):
    template_name = 'reservations/reservation_search.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        search_term = request.POST.get('search', '')
        reservations = Reservation.objects.filter(
            Q(confirmation_number__icontains=search_term) |
            Q(guest__first_name__icontains=search_term) |
            Q(guest__last_name__icontains=search_term) |
            Q(guest__email__icontains=search_term) |
            Q(guest__phone__icontains=search_term)
        )
        
        if request.user.property:
            reservations = reservations.filter(property=request.user.property)
        
        return render(request, self.template_name, {
            'reservations': reservations[:50],
            'search_term': search_term
        })


class GroupBookingListView(LoginRequiredMixin, ListView):
    model = GroupBooking
    template_name = 'reservations/group_list.html'
    context_object_name = 'groups'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = GroupBooking.objects.all()
        if self.request.user.property:
            queryset = queryset.filter(property=self.request.user.property)
        return queryset


class GroupBookingDetailView(LoginRequiredMixin, DetailView):
    model = GroupBooking
    template_name = 'reservations/group_detail.html'
    context_object_name = 'group'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservations'] = self.object.reservations.all()
        return context


class GroupBookingCreateView(LoginRequiredMixin, CreateView):
    model = GroupBooking
    form_class = GroupBookingForm
    template_name = 'reservations/group_form.html'
    success_url = reverse_lazy('reservations:group_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        if self.request.user.property:
            form.instance.property = self.request.user.property
        messages.success(self.request, 'Group booking created successfully.')
        return super().form_valid(form)


class GroupBookingUpdateView(LoginRequiredMixin, UpdateView):
    model = GroupBooking
    form_class = GroupBookingForm
    template_name = 'reservations/group_form.html'
    
    def get_success_url(self):
        return reverse_lazy('reservations:group_detail', kwargs={'pk': self.object.pk})


class ReservationCalendarView(LoginRequiredMixin, View):
    template_name = 'reservations/calendar.html'
    
    def get(self, request):
        # Get date range
        start_date = request.GET.get('start', datetime.now().strftime('%Y-%m-%d'))
        days = int(request.GET.get('days', 14))
        
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = start + timedelta(days=days)
        
        # Get reservations for the period
        reservations = Reservation.objects.filter(
            check_in_date__lte=end,
            check_out_date__gte=start,
            status__in=[Reservation.Status.CONFIRMED, Reservation.Status.CHECKED_IN]
        ).select_related('guest')
        
        if request.user.property:
            reservations = reservations.filter(property=request.user.property)
        
        context = {
            'reservations': reservations,
            'start_date': start,
            'end_date': end,
            'date_range': [start + timedelta(days=i) for i in range(days)]
        }
        return render(request, self.template_name, context)


class AvailabilityView(LoginRequiredMixin, View):
    template_name = 'reservations/availability.html'
    
    def get(self, request):
        from apps.rooms.models import RoomType, Room
        
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        
        room_types = RoomType.objects.filter(is_active=True)
        if request.user.property:
            room_types = room_types.filter(property=request.user.property)
        
        availability = []
        if check_in and check_out:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            
            for room_type in room_types:
                total_rooms = room_type.rooms.filter(is_active=True).count()
                
                # Count booked rooms
                booked_rooms = ReservationRoom.objects.filter(
                    room_type=room_type,
                    reservation__check_in_date__lt=check_out_date,
                    reservation__check_out_date__gt=check_in_date,
                    reservation__status__in=[
                        Reservation.Status.CONFIRMED,
                        Reservation.Status.CHECKED_IN
                    ]
                ).count()
                
                available = total_rooms - booked_rooms
                
                availability.append({
                    'room_type': room_type,
                    'total': total_rooms,
                    'booked': booked_rooms,
                    'available': max(0, available)
                })
        
        context = {
            'room_types': room_types,
            'availability': availability,
            'check_in': check_in,
            'check_out': check_out
        }
        return render(request, self.template_name, context)
