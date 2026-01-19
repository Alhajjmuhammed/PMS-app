"""
Front Desk Operations Models for Hotel PMS
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class CheckIn(models.Model):
    """Check-in record."""
    
    reservation = models.OneToOneField(
        'reservations.Reservation',
        on_delete=models.CASCADE,
        related_name='check_in'
    )
    room = models.ForeignKey(
        'rooms.Room',
        on_delete=models.PROTECT,
        related_name='check_ins'
    )
    guest = models.ForeignKey(
        'guests.Guest',
        on_delete=models.PROTECT,
        related_name='check_ins'
    )
    
    # Check-in details
    check_in_time = models.DateTimeField(_('check-in time'), default=timezone.now)
    expected_check_out = models.DateField(_('expected check-out'))
    
    # ID Verification
    id_type = models.CharField(_('ID type'), max_length=50, blank=True)
    id_number = models.CharField(_('ID number'), max_length=100, blank=True)
    id_expiry = models.DateField(_('ID expiry'), null=True, blank=True)
    
    # Registration
    registration_number = models.CharField(_('registration number'), max_length=50, unique=True)
    registration_card = models.FileField(_('registration card'), upload_to='registration_cards/', blank=True, null=True)
    signature = models.ImageField(_('signature'), upload_to='signatures/', blank=True, null=True)
    
    # Key card
    key_card_number = models.CharField(_('key card number'), max_length=50, blank=True)
    keys_issued = models.PositiveIntegerField(_('keys issued'), default=1)
    
    # Deposit
    deposit_amount = models.DecimalField(_('deposit amount'), max_digits=10, decimal_places=2, default=0)
    deposit_method = models.CharField(_('deposit method'), max_length=50, blank=True)
    
    # Notes
    notes = models.TextField(_('notes'), blank=True)
    
    # Audit
    checked_in_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='performed_check_ins'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('check-in')
        verbose_name_plural = _('check-ins')
        ordering = ['-check_in_time']
    
    def __str__(self):
        return f"{self.registration_number} - {self.guest}"


class CheckOut(models.Model):
    """Check-out record."""
    
    check_in = models.OneToOneField(
        CheckIn,
        on_delete=models.CASCADE,
        related_name='check_out'
    )
    
    # Check-out details
    check_out_time = models.DateTimeField(_('check-out time'), default=timezone.now)
    
    # Billing
    total_charges = models.DecimalField(_('total charges'), max_digits=12, decimal_places=2, default=0)
    total_payments = models.DecimalField(_('total payments'), max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(_('balance'), max_digits=12, decimal_places=2, default=0)
    
    # Key return
    keys_returned = models.PositiveIntegerField(_('keys returned'), default=0)
    
    # Express checkout
    is_express = models.BooleanField(_('express checkout'), default=False)
    
    # Feedback
    rating = models.PositiveSmallIntegerField(_('rating'), null=True, blank=True)
    feedback = models.TextField(_('feedback'), blank=True)
    
    # Notes
    notes = models.TextField(_('notes'), blank=True)
    
    # Audit
    checked_out_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='performed_check_outs'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('check-out')
        verbose_name_plural = _('check-outs')
        ordering = ['-check_out_time']
    
    def __str__(self):
        return f"Check-out: {self.check_in.registration_number}"


class RoomMove(models.Model):
    """Room change/move record."""
    
    check_in = models.ForeignKey(
        CheckIn,
        on_delete=models.CASCADE,
        related_name='room_moves'
    )
    from_room = models.ForeignKey(
        'rooms.Room',
        on_delete=models.PROTECT,
        related_name='moves_from'
    )
    to_room = models.ForeignKey(
        'rooms.Room',
        on_delete=models.PROTECT,
        related_name='moves_to'
    )
    reason = models.CharField(_('reason'), max_length=200)
    move_time = models.DateTimeField(_('move time'), default=timezone.now)
    moved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('room move')
        verbose_name_plural = _('room moves')
        ordering = ['-move_time']
    
    def __str__(self):
        return f"{self.check_in.guest}: {self.from_room} → {self.to_room}"


class WalkIn(models.Model):
    """Walk-in guest record."""
    
    property = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='walk_ins'
    )
    
    # Guest info
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('phone'), max_length=20)
    
    # Stay details
    room_type = models.ForeignKey(
        'rooms.RoomType',
        on_delete=models.PROTECT,
        related_name='walk_ins'
    )
    check_in_date = models.DateField(_('check-in date'))
    check_out_date = models.DateField(_('check-out date'))
    adults = models.PositiveIntegerField(_('adults'), default=1)
    children = models.PositiveIntegerField(_('children'), default=0)
    
    # Rate
    rate_per_night = models.DecimalField(_('rate per night'), max_digits=10, decimal_places=2)
    
    # Status
    is_converted = models.BooleanField(_('converted to reservation'), default=False)
    reservation = models.OneToOneField(
        'reservations.Reservation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='walk_in'
    )
    
    # Notes
    notes = models.TextField(_('notes'), blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('walk-in')
        verbose_name_plural = _('walk-ins')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Walk-in: {self.first_name} {self.last_name}"


class GuestMessage(models.Model):
    """Messages for guests."""
    
    class MessageType(models.TextChoices):
        PHONE = 'PHONE', _('Phone Message')
        PACKAGE = 'PACKAGE', _('Package')
        FAX = 'FAX', _('Fax')
        VISITOR = 'VISITOR', _('Visitor')
        OTHER = 'OTHER', _('Other')
    
    check_in = models.ForeignKey(
        CheckIn,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    message_type = models.CharField(
        _('type'),
        max_length=20,
        choices=MessageType.choices,
        default=MessageType.PHONE
    )
    message = models.TextField(_('message'))
    from_name = models.CharField(_('from'), max_length=200, blank=True)
    from_contact = models.CharField(_('contact'), max_length=100, blank=True)
    
    # Status
    is_delivered = models.BooleanField(_('delivered'), default=False)
    delivered_at = models.DateTimeField(_('delivered at'), null=True, blank=True)
    
    # Audit
    taken_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('guest message')
        verbose_name_plural = _('guest messages')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message for {self.check_in.guest}: {self.message_type}"
