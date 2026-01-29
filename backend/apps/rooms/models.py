"""
Room Models for Hotel PMS
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class RoomType(models.Model):
    """Room type/category model."""
    
    hotel = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='room_types'
    )
    name = models.CharField(_('room type name'), max_length=100)
    code = models.CharField(_('room type code'), max_length=20)
    description = models.TextField(_('description'), blank=True)
    
    # Capacity
    max_occupancy = models.PositiveIntegerField(_('max occupancy'), default=2)
    max_adults = models.PositiveIntegerField(_('max adults'), default=2)
    max_children = models.PositiveIntegerField(_('max children'), default=1)
    
    # Size
    size_sqm = models.DecimalField(_('size (sqm)'), max_digits=6, decimal_places=2, null=True, blank=True)
    bed_type = models.CharField(_('bed type'), max_length=100, blank=True)
    
    # Pricing
    base_rate = models.DecimalField(_('base rate'), max_digits=10, decimal_places=2, default=0)
    extra_adult_rate = models.DecimalField(_('extra adult rate'), max_digits=10, decimal_places=2, default=0)
    extra_child_rate = models.DecimalField(_('extra child rate'), max_digits=10, decimal_places=2, default=0)
    
    # Media
    image = models.ImageField(_('image'), upload_to='room_types/', blank=True, null=True)
    
    # Settings
    sort_order = models.PositiveIntegerField(_('sort order'), default=0)
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('room type')
        verbose_name_plural = _('room types')
        unique_together = ['hotel', 'code']
        ordering = ['hotel', 'sort_order', 'name']
    
    def __str__(self):
        return f"{self.hotel.name} - {self.name}"


class RoomAmenity(models.Model):
    """Amenities that can be assigned to rooms."""
    
    class AmenityCategory(models.TextChoices):
        BATHROOM = 'BATHROOM', _('Bathroom')
        BEDROOM = 'BEDROOM', _('Bedroom')
        ENTERTAINMENT = 'ENTERTAINMENT', _('Entertainment')
        KITCHEN = 'KITCHEN', _('Kitchen')
        TECHNOLOGY = 'TECHNOLOGY', _('Technology')
        COMFORT = 'COMFORT', _('Comfort')
        VIEW = 'VIEW', _('View')
        OTHER = 'OTHER', _('Other')
    
    name = models.CharField(_('amenity name'), max_length=100)
    code = models.CharField(_('amenity code'), max_length=20, unique=True)
    category = models.CharField(
        _('category'),
        max_length=20,
        choices=AmenityCategory.choices,
        default=AmenityCategory.OTHER
    )
    description = models.TextField(_('description'), blank=True)
    icon = models.CharField(_('icon'), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _('room amenity')
        verbose_name_plural = _('room amenities')
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name


class RoomTypeAmenity(models.Model):
    """Amenities assigned to room types."""
    
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        related_name='amenities'
    )
    amenity = models.ForeignKey(
        RoomAmenity,
        on_delete=models.CASCADE,
        related_name='room_types'
    )
    
    class Meta:
        verbose_name = _('room type amenity')
        verbose_name_plural = _('room type amenities')
        unique_together = ['room_type', 'amenity']
    
    def __str__(self):
        return f"{self.room_type.name} - {self.amenity.name}"


class Room(models.Model):
    """Individual room model."""
    
    class RoomStatus(models.TextChoices):
        VACANT_CLEAN = 'VC', _('Vacant Clean')
        VACANT_DIRTY = 'VD', _('Vacant Dirty')
        OCCUPIED_CLEAN = 'OC', _('Occupied Clean')
        OCCUPIED_DIRTY = 'OD', _('Occupied Dirty')
        OUT_OF_ORDER = 'OOO', _('Out of Order')
        OUT_OF_SERVICE = 'OOS', _('Out of Service')
    
    class FrontOfficeStatus(models.TextChoices):
        VACANT = 'VACANT', _('Vacant')
        OCCUPIED = 'OCCUPIED', _('Occupied')
        RESERVED = 'RESERVED', _('Reserved')
        BLOCKED = 'BLOCKED', _('Blocked')
        DUE_OUT = 'DUE_OUT', _('Due Out')
        CHECKED_OUT = 'CHECKED_OUT', _('Checked Out')
    
    hotel = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='rooms'
    )
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.PROTECT,
        related_name='rooms'
    )
    building = models.ForeignKey(
        'properties.Building',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rooms'
    )
    floor = models.ForeignKey(
        'properties.Floor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rooms'
    )
    
    room_number = models.CharField(_('room number'), max_length=20)
    name = models.CharField(_('room name'), max_length=100, blank=True)
    description = models.TextField(_('description'), blank=True)
    
    # Status
    status = models.CharField(
        _('housekeeping status'),
        max_length=5,
        choices=RoomStatus.choices,
        default=RoomStatus.VACANT_CLEAN
    )
    fo_status = models.CharField(
        _('front office status'),
        max_length=20,
        choices=FrontOfficeStatus.choices,
        default=FrontOfficeStatus.VACANT
    )
    
    # Features
    is_smoking = models.BooleanField(_('smoking allowed'), default=False)
    is_accessible = models.BooleanField(_('accessible'), default=False)
    is_connecting = models.BooleanField(_('connecting room'), default=False)
    connecting_room = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='connected_rooms'
    )
    
    # Settings
    is_active = models.BooleanField(_('active'), default=True)
    sort_order = models.PositiveIntegerField(_('sort order'), default=0)
    notes = models.TextField(_('notes'), blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('room')
        verbose_name_plural = _('rooms')
        unique_together = ['hotel', 'room_number']
        ordering = ['hotel', 'room_number']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['room_number']),
            models.Index(fields=['hotel', 'status']),
        ]
    
    def __str__(self):
        return f"{self.hotel.name} - Room {self.room_number}"
    
    @property
    def is_available(self):
        return self.fo_status == self.FrontOfficeStatus.VACANT and self.status in [
            self.RoomStatus.VACANT_CLEAN
        ]
    
    @property
    def is_clean(self):
        return self.status in [self.RoomStatus.VACANT_CLEAN, self.RoomStatus.OCCUPIED_CLEAN]


class RoomBlock(models.Model):
    """Block rooms for maintenance or other purposes."""
    
    class BlockReason(models.TextChoices):
        MAINTENANCE = 'MAINTENANCE', _('Maintenance')
        RENOVATION = 'RENOVATION', _('Renovation')
        VIP_BLOCK = 'VIP_BLOCK', _('VIP Block')
        INVENTORY_CONTROL = 'INVENTORY', _('Inventory Control')
        OTHER = 'OTHER', _('Other')
    
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='blocks'
    )
    reason = models.CharField(
        _('reason'),
        max_length=20,
        choices=BlockReason.choices,
        default=BlockReason.MAINTENANCE
    )
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    notes = models.TextField(_('notes'), blank=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='room_blocks'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('room block')
        verbose_name_plural = _('room blocks')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"Room {self.room.room_number} blocked: {self.start_date} - {self.end_date}"


class RoomStatusLog(models.Model):
    """Track room status changes."""
    
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='status_logs'
    )
    previous_status = models.CharField(_('previous status'), max_length=5)
    new_status = models.CharField(_('new status'), max_length=5)
    changed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='room_status_changes'
    )
    notes = models.TextField(_('notes'), blank=True)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('room status log')
        verbose_name_plural = _('room status logs')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Room {self.room.room_number}: {self.previous_status} -> {self.new_status}"


class RoomImage(models.Model):
    """Room image model for gallery."""
    
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(_('image'), upload_to='rooms/images/')
    caption = models.CharField(_('caption'), max_length=200, blank=True)
    is_primary = models.BooleanField(_('primary image'), default=False)
    sort_order = models.PositiveIntegerField(_('sort order'), default=0)
    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)
    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_room_images'
    )
    
    class Meta:
        verbose_name = _('room image')
        verbose_name_plural = _('room images')
        ordering = ['-is_primary', 'sort_order', '-uploaded_at']
    
    def __str__(self):
        return f"Image for Room {self.room.room_number}"
    
    def save(self, *args, **kwargs):
        # If this is set as primary, unset other primary images for this room
        if self.is_primary:
            RoomImage.objects.filter(room=self.room, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)
