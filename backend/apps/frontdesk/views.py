from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import date, timedelta
import uuid

from apps.reservations.models import Reservation
from apps.rooms.models import Room, RoomType
from apps.guests.models import Guest
from .models import CheckIn, CheckOut, RoomMove, WalkIn, GuestMessage
from .forms import CheckInForm, CheckOutForm, RoomMoveForm, WalkInForm, GuestMessageForm


class DashboardView(LoginRequiredMixin, View):
    """Main front desk dashboard."""
    template_name = 'frontdesk/dashboard.html'
    
    def get(self, request):
        today = date.today()
        property_filter = {}
        if request.user.property:
            property_filter = {'property': request.user.property}
        
        # Today's statistics
        arrivals = Reservation.objects.filter(
            check_in_date=today,
            status__in=[Reservation.Status.CONFIRMED, Reservation.Status.PENDING],
            **property_filter
        ).count()
        
        departures = CheckIn.objects.filter(
            expected_check_out=today,
            check_out__isnull=True,
            **({'room__property': request.user.property} if request.user.property else {})
        ).count()
        
        in_house = CheckIn.objects.filter(
            check_out__isnull=True,
            **({'room__property': request.user.property} if request.user.property else {})
        ).count()
        
        # Room statistics
        rooms = Room.objects.filter(is_active=True, **property_filter)
        room_stats = {
            'total': rooms.count(),
            'occupied': rooms.filter(fo_status=Room.FrontOfficeStatus.OCCUPIED).count(),
            'vacant_clean': rooms.filter(status=Room.RoomStatus.VACANT_CLEAN).count(),
            'vacant_dirty': rooms.filter(status=Room.RoomStatus.VACANT_DIRTY).count(),
            'out_of_order': rooms.filter(status=Room.RoomStatus.OUT_OF_ORDER).count(),
        }
        
        # Recent check-ins
        recent_check_ins = CheckIn.objects.select_related('guest', 'room').order_by('-check_in_time')[:5]
        
        # Pending arrivals
        pending_arrivals = Reservation.objects.filter(
            check_in_date=today,
            status=Reservation.Status.CONFIRMED,
            **property_filter
        ).select_related('guest')[:10]
        
        context = {
            'today': today,
            'arrivals': arrivals,
            'departures': departures,
            'in_house': in_house,
            'room_stats': room_stats,
            'recent_check_ins': recent_check_ins,
            'pending_arrivals': pending_arrivals,
        }
        return render(request, self.template_name, context)


class ArrivalsView(LoginRequiredMixin, ListView):
    """Today's arrivals."""
    template_name = 'frontdesk/arrivals.html'
    context_object_name = 'arrivals'
    
    def get_queryset(self):
        date_filter = self.request.GET.get('date', date.today())
        queryset = Reservation.objects.filter(
            check_in_date=date_filter,
            status__in=[Reservation.Status.CONFIRMED, Reservation.Status.PENDING]
        ).select_related('guest')
        
        if self.request.user.property:
            queryset = queryset.filter(property=self.request.user.property)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_date'] = self.request.GET.get('date', date.today())
        return context


class DeparturesView(LoginRequiredMixin, ListView):
    """Today's departures."""
    template_name = 'frontdesk/departures.html'
    context_object_name = 'departures'
    
    def get_queryset(self):
        date_filter = self.request.GET.get('date', date.today())
        queryset = CheckIn.objects.filter(
            expected_check_out=date_filter,
            check_out__isnull=True
        ).select_related('guest', 'room', 'reservation')
        
        if self.request.user.property:
            queryset = queryset.filter(room__property=self.request.user.property)
        
        return queryset


class InHouseView(LoginRequiredMixin, ListView):
    """In-house guests."""
    template_name = 'frontdesk/in_house.html'
    context_object_name = 'guests'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = CheckIn.objects.filter(
            check_out__isnull=True
        ).select_related('guest', 'room', 'reservation')
        
        if self.request.user.property:
            queryset = queryset.filter(room__property=self.request.user.property)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(guest__first_name__icontains=search) |
                Q(guest__last_name__icontains=search) |
                Q(room__room_number__icontains=search) |
                Q(registration_number__icontains=search)
            )
        
        return queryset.order_by('room__room_number')


class CheckInView(LoginRequiredMixin, View):
    """Process check-in."""
    template_name = 'frontdesk/check_in.html'
    
    def get(self, request, reservation_pk):
        reservation = get_object_or_404(Reservation, pk=reservation_pk)
        
        # Get available rooms for this room type
        available_rooms = Room.objects.filter(
            property=reservation.property,
            status=Room.RoomStatus.VACANT_CLEAN,
            fo_status=Room.FrontOfficeStatus.VACANT,
            is_active=True
        )
        
        form = CheckInForm(initial={
            'reservation': reservation,
            'guest': reservation.guest,
            'expected_check_out': reservation.check_out_date,
        })
        
        context = {
            'reservation': reservation,
            'form': form,
            'available_rooms': available_rooms,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, reservation_pk):
        reservation = get_object_or_404(Reservation, pk=reservation_pk)
        form = CheckInForm(request.POST, request.FILES)
        
        if form.is_valid():
            check_in = form.save(commit=False)
            check_in.reservation = reservation
            check_in.guest = reservation.guest
            check_in.registration_number = f"REG-{uuid.uuid4().hex[:8].upper()}"
            check_in.checked_in_by = request.user
            check_in.save()
            
            # Update reservation status
            reservation.status = Reservation.Status.CHECKED_IN
            reservation.save()
            
            # Update room status
            room = check_in.room
            room.fo_status = Room.FrontOfficeStatus.OCCUPIED
            room.status = Room.RoomStatus.OCCUPIED_CLEAN
            room.save()
            
            messages.success(request, f'Guest checked in successfully. Registration: {check_in.registration_number}')
            return redirect('frontdesk:dashboard')
        
        context = {
            'reservation': reservation,
            'form': form,
            'available_rooms': Room.objects.filter(
                property=reservation.property,
                status=Room.RoomStatus.VACANT_CLEAN,
                is_active=True
            ),
        }
        return render(request, self.template_name, context)


class CheckOutView(LoginRequiredMixin, View):
    """Process check-out."""
    template_name = 'frontdesk/check_out.html'
    
    def get(self, request, check_in_pk):
        check_in = get_object_or_404(CheckIn, pk=check_in_pk)
        
        # Calculate charges from folio
        from apps.billing.models import Folio
        try:
            folio = check_in.reservation.folio
            total_charges = folio.total_charges
            total_payments = folio.total_payments
            balance = folio.balance
        except:
            total_charges = 0
            total_payments = 0
            balance = 0
        
        form = CheckOutForm(initial={
            'total_charges': total_charges,
            'total_payments': total_payments,
            'balance': balance,
            'keys_returned': check_in.keys_issued,
        })
        
        context = {
            'check_in': check_in,
            'form': form,
            'total_charges': total_charges,
            'total_payments': total_payments,
            'balance': balance,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, check_in_pk):
        check_in = get_object_or_404(CheckIn, pk=check_in_pk)
        form = CheckOutForm(request.POST)
        
        if form.is_valid():
            check_out = form.save(commit=False)
            check_out.check_in = check_in
            check_out.checked_out_by = request.user
            check_out.save()
            
            # Update reservation status
            check_in.reservation.status = Reservation.Status.CHECKED_OUT
            check_in.reservation.save()
            
            # Update room status
            room = check_in.room
            room.fo_status = Room.FrontOfficeStatus.CHECKED_OUT
            room.status = Room.RoomStatus.VACANT_DIRTY
            room.save()
            
            messages.success(request, 'Guest checked out successfully.')
            return redirect('frontdesk:dashboard')
        
        context = {
            'check_in': check_in,
            'form': form,
        }
        return render(request, self.template_name, context)


class ExpressCheckOutView(LoginRequiredMixin, View):
    """Express check-out."""
    
    def post(self, request, check_in_pk):
        check_in = get_object_or_404(CheckIn, pk=check_in_pk)
        
        # Create check-out record
        check_out = CheckOut.objects.create(
            check_in=check_in,
            is_express=True,
            keys_returned=check_in.keys_issued,
            checked_out_by=request.user
        )
        
        # Update statuses
        check_in.reservation.status = Reservation.Status.CHECKED_OUT
        check_in.reservation.save()
        
        room = check_in.room
        room.fo_status = Room.FrontOfficeStatus.CHECKED_OUT
        room.status = Room.RoomStatus.VACANT_DIRTY
        room.save()
        
        messages.success(request, 'Express check-out completed.')
        return redirect('frontdesk:departures')


class RoomMoveView(LoginRequiredMixin, View):
    """Room move/change."""
    template_name = 'frontdesk/room_move.html'
    
    def get(self, request, check_in_pk):
        check_in = get_object_or_404(CheckIn, pk=check_in_pk)
        
        available_rooms = Room.objects.filter(
            property=check_in.room.property,
            status=Room.RoomStatus.VACANT_CLEAN,
            fo_status=Room.FrontOfficeStatus.VACANT,
            is_active=True
        ).exclude(pk=check_in.room.pk)
        
        form = RoomMoveForm()
        
        context = {
            'check_in': check_in,
            'form': form,
            'available_rooms': available_rooms,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, check_in_pk):
        check_in = get_object_or_404(CheckIn, pk=check_in_pk)
        form = RoomMoveForm(request.POST)
        
        if form.is_valid():
            from_room = check_in.room
            to_room = form.cleaned_data['to_room']
            
            # Create move record
            RoomMove.objects.create(
                check_in=check_in,
                from_room=from_room,
                to_room=to_room,
                reason=form.cleaned_data['reason'],
                moved_by=request.user,
                notes=form.cleaned_data.get('notes', '')
            )
            
            # Update old room
            from_room.fo_status = Room.FrontOfficeStatus.CHECKED_OUT
            from_room.status = Room.RoomStatus.VACANT_DIRTY
            from_room.save()
            
            # Update new room
            to_room.fo_status = Room.FrontOfficeStatus.OCCUPIED
            to_room.status = Room.RoomStatus.OCCUPIED_CLEAN
            to_room.save()
            
            # Update check-in
            check_in.room = to_room
            check_in.save()
            
            messages.success(request, f'Guest moved from {from_room.room_number} to {to_room.room_number}')
            return redirect('frontdesk:in_house')
        
        context = {
            'check_in': check_in,
            'form': form,
        }
        return render(request, self.template_name, context)


class RoomAssignmentView(LoginRequiredMixin, View):
    """Room assignment view."""
    template_name = 'frontdesk/room_assignment.html'
    
    def get(self, request):
        # Get unassigned reservations arriving today
        today = date.today()
        unassigned = Reservation.objects.filter(
            check_in_date=today,
            status=Reservation.Status.CONFIRMED,
            rooms__room__isnull=True
        ).select_related('guest')
        
        if request.user.property:
            unassigned = unassigned.filter(property=request.user.property)
        
        context = {
            'unassigned_reservations': unassigned,
        }
        return render(request, self.template_name, context)


class WalkInListView(LoginRequiredMixin, ListView):
    """List walk-ins."""
    model = WalkIn
    template_name = 'frontdesk/walk_in_list.html'
    context_object_name = 'walk_ins'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = WalkIn.objects.all()
        if self.request.user.property:
            queryset = queryset.filter(property=self.request.user.property)
        return queryset.order_by('-created_at')


class WalkInCreateView(LoginRequiredMixin, CreateView):
    """Create walk-in."""
    model = WalkIn
    form_class = WalkInForm
    template_name = 'frontdesk/walk_in_form.html'
    success_url = reverse_lazy('frontdesk:walk_in_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        if self.request.user.property:
            form.instance.property = self.request.user.property
        messages.success(self.request, 'Walk-in record created.')
        return super().form_valid(form)


class WalkInCheckInView(LoginRequiredMixin, View):
    """Check-in a walk-in guest directly."""
    template_name = 'frontdesk/walk_in_check_in.html'
    
    def get(self, request):
        form = WalkInForm()
        context = {'form': form}
        return render(request, self.template_name, context)


class GuestMessageListView(LoginRequiredMixin, ListView):
    """List guest messages."""
    model = GuestMessage
    template_name = 'frontdesk/message_list.html'
    context_object_name = 'messages'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = GuestMessage.objects.select_related('check_in__guest').all()
        
        undelivered_only = self.request.GET.get('undelivered')
        if undelivered_only:
            queryset = queryset.filter(is_delivered=False)
        
        return queryset.order_by('-created_at')


class GuestMessageCreateView(LoginRequiredMixin, CreateView):
    """Create guest message."""
    model = GuestMessage
    form_class = GuestMessageForm
    template_name = 'frontdesk/message_form.html'
    
    def form_valid(self, form):
        check_in = get_object_or_404(CheckIn, pk=self.kwargs['check_in_pk'])
        form.instance.check_in = check_in
        form.instance.taken_by = self.request.user
        messages.success(self.request, 'Message recorded.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('frontdesk:message_list')


class GuestMessageDeliverView(LoginRequiredMixin, View):
    """Mark message as delivered."""
    
    def post(self, request, pk):
        message = get_object_or_404(GuestMessage, pk=pk)
        message.is_delivered = True
        message.delivered_at = timezone.now()
        message.save()
        messages.success(request, 'Message marked as delivered.')
        return redirect('frontdesk:message_list')


class RoomGridView(LoginRequiredMixin, View):
    """Visual room grid."""
    template_name = 'frontdesk/room_grid.html'
    
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
            'status_colors': {
                'VC': '#28a745',  # green
                'VD': '#ffc107',  # yellow
                'OC': '#007bff',  # blue
                'OD': '#17a2b8',  # cyan
                'OOO': '#dc3545',  # red
                'OOS': '#6c757d',  # gray
            }
        }
        return render(request, self.template_name, context)
