"""
Reservation Models for Hotel PMS
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid


class Reservation(models.Model):
    """Main reservation model."""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        CHECKED_IN = 'CHECKED_IN', _('Checked In')
        CHECKED_OUT = 'CHECKED_OUT', _('Checked Out')
        CANCELLED = 'CANCELLED', _('Cancelled')
        NO_SHOW = 'NO_SHOW', _('No Show')
        WAITLIST = 'WAITLIST', _('Waitlist')
    
    class Source(models.TextChoices):
        DIRECT = 'DIRECT', _('Direct Booking')
        PHONE = 'PHONE', _('Phone')
        EMAIL = 'EMAIL', _('Email')
        WALK_IN = 'WALK_IN', _('Walk-in')
        WEBSITE = 'WEBSITE', _('Website')
        OTA = 'OTA', _('OTA')
        GDS = 'GDS', _('GDS')
        CORPORATE = 'CORPORATE', _('Corporate')
        TRAVEL_AGENT = 'TRAVEL_AGENT', _('Travel Agent')
    
    # Identifiers
    confirmation_number = models.CharField(
        _('confirmation number'),
        max_length=50,
        unique=True,
        editable=False
    )
    external_id = models.CharField(
        _('external ID'),
        max_length=100,
        blank=True,
        help_text=_('ID from OTA or channel manager')
    )
    
    # Property & Guest
    hotel = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    guest = models.ForeignKey(
        'guests.Guest',
        on_delete=models.PROTECT,
        related_name='reservations'
    )
    company = models.ForeignKey(
        'guests.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservations'
    )
    
    # Dates
    check_in_date = models.DateField(_('check-in date'))
    check_out_date = models.DateField(_('check-out date'))
    arrival_time = models.TimeField(_('arrival time'), null=True, blank=True)
    departure_time = models.TimeField(_('departure time'), null=True, blank=True)
    
    # Status
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    source = models.CharField(
        _('booking source'),
        max_length=20,
        choices=Source.choices,
        default=Source.DIRECT
    )
    
    # Occupancy
    adults = models.PositiveIntegerField(_('adults'), default=1)
    children = models.PositiveIntegerField(_('children'), default=0)
    infants = models.PositiveIntegerField(_('infants'), default=0)
    
    # Special Requests
    special_requests = models.TextField(_('special requests'), blank=True)
    internal_notes = models.TextField(_('internal notes'), blank=True)
    
    # Financial
    total_amount = models.DecimalField(
        _('total amount'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    deposit_amount = models.DecimalField(
        _('deposit amount'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    deposit_paid = models.BooleanField(_('deposit paid'), default=False)
    
    # Group Booking
    group = models.ForeignKey(
        'GroupBooking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservations'
    )
    
    # Rate & Channel
    rate_plan = models.ForeignKey(
        'rates.RatePlan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservations'
    )
    channel = models.ForeignKey(
        'channels.Channel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservations'
    )
    
    # Audit
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_reservations'
    )
    modified_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='modified_reservations'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('reservation')
        verbose_name_plural = _('reservations')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.confirmation_number} - {self.guest}"
    
    def save(self, *args, **kwargs):
        if not self.confirmation_number:
            self.confirmation_number = self.generate_confirmation_number()
        super().save(*args, **kwargs)
    
    def generate_confirmation_number(self):
        """Generate unique confirmation number."""
        prefix = self.hotel.code if self.hotel_id else 'RES'
        timestamp = timezone.now().strftime('%y%m%d')
        unique_id = uuid.uuid4().hex[:6].upper()
        return f"{prefix}{timestamp}{unique_id}"
    
    @property
    def nights(self):
        return (self.check_out_date - self.check_in_date).days
    
    @property
    def is_active(self):
        return self.status in [self.Status.PENDING, self.Status.CONFIRMED, self.Status.CHECKED_IN]


class ReservationRoom(models.Model):
    """Rooms associated with a reservation."""
    
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name='rooms'
    )
    room_type = models.ForeignKey(
        'rooms.RoomType',
        on_delete=models.PROTECT,
        related_name='reservation_rooms'
    )
    room = models.ForeignKey(
        'rooms.Room',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservation_rooms'
    )
    
    # Rate
    rate_per_night = models.DecimalField(
        _('rate per night'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_rate = models.DecimalField(
        _('total rate'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # Occupancy
    adults = models.PositiveIntegerField(_('adults'), default=1)
    children = models.PositiveIntegerField(_('children'), default=0)
    
    # Guest(s) for this room
    guest_name = models.CharField(_('guest name'), max_length=200, blank=True)
    
    class Meta:
        verbose_name = _('reservation room')
        verbose_name_plural = _('reservation rooms')
    
    def __str__(self):
        room_info = self.room.room_number if self.room else self.room_type.name
        return f"{self.reservation.confirmation_number} - {room_info}"


class ReservationRateDetail(models.Model):
    """Daily rate breakdown for reservation rooms."""
    
    reservation_room = models.ForeignKey(
        ReservationRoom,
        on_delete=models.CASCADE,
        related_name='rate_details'
    )
    date = models.DateField(_('date'))
    rate = models.DecimalField(_('rate'), max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _('reservation rate detail')
        verbose_name_plural = _('reservation rate details')
        unique_together = ['reservation_room', 'date']
        ordering = ['date']
    
    def __str__(self):
        return f"{self.reservation_room} - {self.date}: {self.rate}"


class GroupBooking(models.Model):
    """Group booking/block model."""
    
    class Status(models.TextChoices):
        TENTATIVE = 'TENTATIVE', _('Tentative')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        CANCELLED = 'CANCELLED', _('Cancelled')
    
    hotel = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='group_bookings'
    )
    name = models.CharField(_('group name'), max_length=200)
    code = models.CharField(_('group code'), max_length=50, unique=True)
    
    # Contact
    contact_name = models.CharField(_('contact name'), max_length=200)
    contact_email = models.EmailField(_('contact email'), blank=True)
    contact_phone = models.CharField(_('contact phone'), max_length=20, blank=True)
    company = models.ForeignKey(
        'guests.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='group_bookings'
    )
    
    # Dates
    check_in_date = models.DateField(_('check-in date'))
    check_out_date = models.DateField(_('check-out date'))
    cutoff_date = models.DateField(_('cutoff date'), null=True, blank=True)
    
    # Rooms
    rooms_blocked = models.PositiveIntegerField(_('rooms blocked'), default=0)
    rooms_picked_up = models.PositiveIntegerField(_('rooms picked up'), default=0)
    
    # Status
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.TENTATIVE
    )
    
    # Financial
    group_rate = models.DecimalField(
        _('group rate'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    deposit_required = models.DecimalField(
        _('deposit required'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    # Notes
    notes = models.TextField(_('notes'), blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_groups'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('group booking')
        verbose_name_plural = _('group bookings')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ReservationLog(models.Model):
    """Track reservation changes."""
    
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(_('action'), max_length=100)
    old_value = models.TextField(_('old value'), blank=True)
    new_value = models.TextField(_('new value'), blank=True)
    notes = models.TextField(_('notes'), blank=True)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('reservation log')
        verbose_name_plural = _('reservation logs')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.reservation.confirmation_number} - {self.action}"
