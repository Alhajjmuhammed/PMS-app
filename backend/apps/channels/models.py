"""
Channel Manager Models for OTA Integration
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Channel(models.Model):
    """Distribution channel (OTA, GDS, etc.)."""
    
    class ChannelType(models.TextChoices):
        OTA = 'OTA', _('Online Travel Agency')
        GDS = 'GDS', _('Global Distribution System')
        DIRECT = 'DIRECT', _('Direct Booking')
        META = 'META', _('Metasearch')
        CORPORATE = 'CORPORATE', _('Corporate Portal')
    
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=20, unique=True)
    channel_type = models.CharField(_('type'), max_length=20, choices=ChannelType.choices)
    
    # Commission
    commission_percent = models.DecimalField(_('commission %'), max_digits=5, decimal_places=2, default=0)
    
    # API connection
    api_url = models.URLField(_('API URL'), blank=True)
    api_key = models.CharField(_('API key'), max_length=255, blank=True)
    api_secret = models.CharField(_('API secret'), max_length=255, blank=True)
    
    logo = models.ImageField(_('logo'), upload_to='channels/', blank=True, null=True)
    
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('channel')
        verbose_name_plural = _('channels')
    
    def __str__(self):
        return self.name


class PropertyChannel(models.Model):
    """Property-channel connection."""
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='channels')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='properties')
    
    property_code = models.CharField(_('property code on channel'), max_length=100)
    
    # Rate mapping
    rate_plan = models.ForeignKey('rates.RatePlan', on_delete=models.SET_NULL, null=True, blank=True)
    rate_markup = models.DecimalField(_('rate markup %'), max_digits=5, decimal_places=2, default=0)
    
    # Availability settings
    min_availability = models.PositiveIntegerField(_('min availability'), default=0)
    max_availability = models.PositiveIntegerField(_('max availability'), null=True, blank=True)
    
    # Sync settings
    sync_rates = models.BooleanField(_('sync rates'), default=True)
    sync_availability = models.BooleanField(_('sync availability'), default=True)
    sync_restrictions = models.BooleanField(_('sync restrictions'), default=True)
    
    last_sync = models.DateTimeField(_('last sync'), null=True, blank=True)
    
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('property channel')
        verbose_name_plural = _('property channels')
        unique_together = ['property', 'channel']
    
    def __str__(self):
        return f"{self.property.name} - {self.channel.name}"


class RoomTypeMapping(models.Model):
    """Maps room types to channel room types."""
    
    property_channel = models.ForeignKey(PropertyChannel, on_delete=models.CASCADE, related_name='room_mappings')
    room_type = models.ForeignKey('rooms.RoomType', on_delete=models.CASCADE)
    channel_room_code = models.CharField(_('channel room code'), max_length=100)
    channel_room_name = models.CharField(_('channel room name'), max_length=200)
    
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('room type mapping')
        verbose_name_plural = _('room type mappings')
        unique_together = ['property_channel', 'room_type']
    
    def __str__(self):
        return f"{self.room_type.code} -> {self.channel_room_code}"


class RatePlanMapping(models.Model):
    """Maps rate plans to channel rates."""
    
    property_channel = models.ForeignKey(PropertyChannel, on_delete=models.CASCADE, related_name='rate_mappings')
    rate_plan = models.ForeignKey('rates.RatePlan', on_delete=models.CASCADE)
    channel_rate_code = models.CharField(_('channel rate code'), max_length=100)
    channel_rate_name = models.CharField(_('channel rate name'), max_length=200)
    
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('rate plan mapping')
        verbose_name_plural = _('rate plan mappings')
        unique_together = ['property_channel', 'rate_plan']
    
    def __str__(self):
        return f"{self.rate_plan.code} -> {self.channel_rate_code}"


class AvailabilityUpdate(models.Model):
    """Availability update log."""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        SENT = 'SENT', _('Sent')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        FAILED = 'FAILED', _('Failed')
    
    property_channel = models.ForeignKey(PropertyChannel, on_delete=models.CASCADE, related_name='availability_updates')
    room_type = models.ForeignKey('rooms.RoomType', on_delete=models.CASCADE)
    
    date = models.DateField(_('date'))
    availability = models.PositiveIntegerField(_('availability'))
    
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(_('error message'), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(_('sent at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('availability update')
        verbose_name_plural = _('availability updates')
        ordering = ['-created_at']


class RateUpdate(models.Model):
    """Rate update log."""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        SENT = 'SENT', _('Sent')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        FAILED = 'FAILED', _('Failed')
    
    property_channel = models.ForeignKey(PropertyChannel, on_delete=models.CASCADE, related_name='rate_updates')
    room_type = models.ForeignKey('rooms.RoomType', on_delete=models.CASCADE)
    rate_plan = models.ForeignKey('rates.RatePlan', on_delete=models.CASCADE)
    
    date = models.DateField(_('date'))
    rate = models.DecimalField(_('rate'), max_digits=10, decimal_places=2)
    
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(_('error message'), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(_('sent at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('rate update')
        verbose_name_plural = _('rate updates')
        ordering = ['-created_at']


class ChannelReservation(models.Model):
    """Reservation received from channel."""
    
    class Status(models.TextChoices):
        RECEIVED = 'RECEIVED', _('Received')
        PROCESSED = 'PROCESSED', _('Processed')
        FAILED = 'FAILED', _('Failed')
        CANCELLED = 'CANCELLED', _('Cancelled')
    
    property_channel = models.ForeignKey(PropertyChannel, on_delete=models.CASCADE, related_name='reservations')
    channel_booking_id = models.CharField(_('channel booking ID'), max_length=100)
    
    # Link to actual reservation
    reservation = models.ForeignKey('reservations.Reservation', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Raw data
    raw_data = models.JSONField(_('raw data'), default=dict)
    
    # Parsed data
    guest_name = models.CharField(_('guest name'), max_length=200)
    check_in_date = models.DateField(_('check in'))
    check_out_date = models.DateField(_('check out'))
    room_type_code = models.CharField(_('room type'), max_length=100)
    rate_amount = models.DecimalField(_('rate'), max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(_('total'), max_digits=10, decimal_places=2)
    
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.RECEIVED)
    error_message = models.TextField(_('error message'), blank=True)
    
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('channel reservation')
        verbose_name_plural = _('channel reservations')
        unique_together = ['property_channel', 'channel_booking_id']
        ordering = ['-received_at']
    
    def __str__(self):
        return f"{self.property_channel.channel.name} - {self.channel_booking_id}"
