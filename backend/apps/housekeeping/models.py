"""
Housekeeping Models for Hotel PMS
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class HousekeepingTask(models.Model):
    """Housekeeping task model."""
    
    class TaskType(models.TextChoices):
        CLEANING = 'CLEANING', _('Cleaning')
        TURNDOWN = 'TURNDOWN', _('Turndown Service')
        DEEP_CLEAN = 'DEEP_CLEAN', _('Deep Cleaning')
        INSPECTION = 'INSPECTION', _('Inspection')
        LINEN_CHANGE = 'LINEN_CHANGE', _('Linen Change')
        AMENITY_REFILL = 'AMENITY_REFILL', _('Amenity Refill')
        SPECIAL_REQUEST = 'SPECIAL', _('Special Request')
    
    class Priority(models.TextChoices):
        LOW = 'LOW', _('Low')
        NORMAL = 'NORMAL', _('Normal')
        HIGH = 'HIGH', _('High')
        URGENT = 'URGENT', _('Urgent')
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        INSPECTED = 'INSPECTED', _('Inspected')
        CANCELLED = 'CANCELLED', _('Cancelled')
    
    room = models.ForeignKey(
        'rooms.Room',
        on_delete=models.CASCADE,
        related_name='housekeeping_tasks'
    )
    task_type = models.CharField(
        _('task type'),
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.CLEANING
    )
    priority = models.CharField(
        _('priority'),
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_housekeeping_tasks'
    )
    assigned_at = models.DateTimeField(_('assigned at'), null=True, blank=True)
    
    # Schedule
    scheduled_date = models.DateField(_('scheduled date'), default=timezone.now)
    scheduled_time = models.TimeField(_('scheduled time'), null=True, blank=True)
    
    # Progress
    started_at = models.DateTimeField(_('started at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    
    # Inspection
    inspected_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inspected_tasks'
    )
    inspected_at = models.DateTimeField(_('inspected at'), null=True, blank=True)
    inspection_notes = models.TextField(_('inspection notes'), blank=True)
    inspection_passed = models.BooleanField(_('passed inspection'), null=True)
    
    # Notes
    notes = models.TextField(_('notes'), blank=True)
    special_instructions = models.TextField(_('special instructions'), blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_housekeeping_tasks'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('housekeeping task')
        verbose_name_plural = _('housekeeping tasks')
        ordering = ['-scheduled_date', 'priority', 'room__room_number']
    
    def __str__(self):
        return f"{self.room.room_number} - {self.task_type} ({self.status})"


class RoomInspection(models.Model):
    """Room inspection record."""
    
    room = models.ForeignKey(
        'rooms.Room',
        on_delete=models.CASCADE,
        related_name='inspections'
    )
    inspector = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )
    inspection_date = models.DateTimeField(_('inspection date'), default=timezone.now)
    
    # Checklist scores (1-5)
    cleanliness_score = models.PositiveSmallIntegerField(_('cleanliness'), default=5)
    bed_making_score = models.PositiveSmallIntegerField(_('bed making'), default=5)
    bathroom_score = models.PositiveSmallIntegerField(_('bathroom'), default=5)
    amenities_score = models.PositiveSmallIntegerField(_('amenities'), default=5)
    overall_score = models.PositiveSmallIntegerField(_('overall'), default=5)
    
    passed = models.BooleanField(_('passed'), default=True)
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('room inspection')
        verbose_name_plural = _('room inspections')
        ordering = ['-inspection_date']
    
    def __str__(self):
        return f"Inspection: {self.room.room_number} - {self.inspection_date.date()}"


class LinenInventory(models.Model):
    """Linen inventory tracking."""
    
    class LinenType(models.TextChoices):
        BEDSHEET = 'BEDSHEET', _('Bed Sheet')
        DUVET = 'DUVET', _('Duvet Cover')
        PILLOW_CASE = 'PILLOW_CASE', _('Pillow Case')
        BATH_TOWEL = 'BATH_TOWEL', _('Bath Towel')
        HAND_TOWEL = 'HAND_TOWEL', _('Hand Towel')
        FACE_TOWEL = 'FACE_TOWEL', _('Face Towel')
        BATH_MAT = 'BATH_MAT', _('Bath Mat')
        BATHROBE = 'BATHROBE', _('Bathrobe')
    
    hotel = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='linen_inventory'
    )
    linen_type = models.CharField(_('type'), max_length=20, choices=LinenType.choices)
    quantity_total = models.PositiveIntegerField(_('total quantity'), default=0)
    quantity_in_use = models.PositiveIntegerField(_('in use'), default=0)
    quantity_in_laundry = models.PositiveIntegerField(_('in laundry'), default=0)
    quantity_damaged = models.PositiveIntegerField(_('damaged'), default=0)
    reorder_level = models.PositiveIntegerField(_('reorder level'), default=10)
    
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('linen inventory')
        verbose_name_plural = _('linen inventories')
        unique_together = ['hotel', 'linen_type']
    
    def __str__(self):
        return f"{self.hotel.name} - {self.linen_type}"
    
    @property
    def quantity_available(self):
        return self.quantity_total - self.quantity_in_use - self.quantity_in_laundry - self.quantity_damaged


class AmenityInventory(models.Model):
    """Room amenities inventory."""
    
    hotel = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='amenity_inventory'
    )
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=20)
    category = models.CharField(_('category'), max_length=50, blank=True)
    quantity = models.PositiveIntegerField(_('quantity'), default=0)
    reorder_level = models.PositiveIntegerField(_('reorder level'), default=10)
    unit_cost = models.DecimalField(_('unit cost'), max_digits=8, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = _('amenity inventory')
        verbose_name_plural = _('amenity inventories')
        unique_together = ['hotel', 'code']
    
    def __str__(self):
        return f"{self.hotel.name} - {self.name}"


class HousekeepingSchedule(models.Model):
    """Housekeeping staff schedule."""
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='housekeeping_schedules'
    )
    date = models.DateField(_('date'))
    shift_start = models.TimeField(_('shift start'))
    shift_end = models.TimeField(_('shift end'))
    assigned_floor = models.ForeignKey(
        'properties.Floor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('housekeeping schedule')
        verbose_name_plural = _('housekeeping schedules')
        unique_together = ['user', 'date']
        ordering = ['date', 'shift_start']
    
    def __str__(self):
        return f"{self.user} - {self.date}"


class StockMovement(models.Model):
    """Inventory stock movement tracking."""
    
    class MovementType(models.TextChoices):
        RECEIVE = 'RECEIVE', _('Receive')
        ISSUE = 'ISSUE', _('Issue')
        TRANSFER = 'TRANSFER', _('Transfer')
        ADJUST = 'ADJUST', _('Adjustment')
        RETURN = 'RETURN', _('Return')
        DAMAGE = 'DAMAGE', _('Damage')
    
    property = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='stock_movements'
    )
    
    # Reference to either amenity or linen inventory
    amenity_inventory = models.ForeignKey(
        AmenityInventory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='movements'
    )
    linen_inventory = models.ForeignKey(
        LinenInventory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='movements'
    )
    
    movement_type = models.CharField(
        _('movement type'),
        max_length=10,
        choices=MovementType.choices
    )
    quantity = models.IntegerField(_('quantity'))  # Can be negative for issues
    balance_after = models.PositiveIntegerField(_('balance after'))
    
    # Details
    reference = models.CharField(_('reference'), max_length=100, blank=True)
    reason = models.CharField(_('reason'), max_length=200, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    
    # Location
    from_location = models.CharField(_('from location'), max_length=100, blank=True)
    to_location = models.CharField(_('to location'), max_length=100, blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='stock_movements'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('stock movement')
        verbose_name_plural = _('stock movements')
        ordering = ['-created_at']
    
    def __str__(self):
        item = self.amenity_inventory or self.linen_inventory
        return f"{self.movement_type} - {item} - {self.quantity}"
