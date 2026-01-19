"""
Maintenance Models for Hotel PMS
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class MaintenanceRequest(models.Model):
    """Maintenance request/work order."""
    
    class RequestType(models.TextChoices):
        ELECTRICAL = 'ELECTRICAL', _('Electrical')
        PLUMBING = 'PLUMBING', _('Plumbing')
        HVAC = 'HVAC', _('HVAC')
        FURNITURE = 'FURNITURE', _('Furniture')
        APPLIANCE = 'APPLIANCE', _('Appliance')
        STRUCTURAL = 'STRUCTURAL', _('Structural')
        GENERAL = 'GENERAL', _('General')
        PREVENTIVE = 'PREVENTIVE', _('Preventive')
    
    class Priority(models.TextChoices):
        LOW = 'LOW', _('Low')
        MEDIUM = 'MEDIUM', _('Medium')
        HIGH = 'HIGH', _('High')
        EMERGENCY = 'EMERGENCY', _('Emergency')
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        ASSIGNED = 'ASSIGNED', _('Assigned')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        ON_HOLD = 'ON_HOLD', _('On Hold')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')
    
    # Reference
    request_number = models.CharField(_('request number'), max_length=50, unique=True)
    
    # Location
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='maintenance_requests')
    room = models.ForeignKey('rooms.Room', on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_requests')
    location = models.CharField(_('location'), max_length=200, blank=True)
    
    # Request details
    request_type = models.CharField(_('type'), max_length=20, choices=RequestType.choices, default=RequestType.GENERAL)
    priority = models.CharField(_('priority'), max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'))
    
    # Assignment
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_maintenance')
    assigned_at = models.DateTimeField(null=True, blank=True)
    
    # Progress
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(_('resolution notes'), blank=True)
    
    # Cost tracking
    parts_cost = models.DecimalField(_('parts cost'), max_digits=10, decimal_places=2, default=0)
    labor_hours = models.DecimalField(_('labor hours'), max_digits=5, decimal_places=2, default=0)
    
    # Audit
    reported_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='reported_maintenance')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('maintenance request')
        verbose_name_plural = _('maintenance requests')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.request_number} - {self.title}"


class Asset(models.Model):
    """Hotel assets for tracking."""
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='assets')
    name = models.CharField(_('name'), max_length=200)
    code = models.CharField(_('asset code'), max_length=50, unique=True)
    category = models.CharField(_('category'), max_length=100)
    location = models.CharField(_('location'), max_length=200, blank=True)
    room = models.ForeignKey('rooms.Room', on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    
    # Details
    brand = models.CharField(_('brand'), max_length=100, blank=True)
    model = models.CharField(_('model'), max_length=100, blank=True)
    serial_number = models.CharField(_('serial number'), max_length=100, blank=True)
    
    # Dates
    purchase_date = models.DateField(_('purchase date'), null=True, blank=True)
    warranty_expiry = models.DateField(_('warranty expiry'), null=True, blank=True)
    
    # Value
    purchase_cost = models.DecimalField(_('purchase cost'), max_digits=12, decimal_places=2, default=0)
    current_value = models.DecimalField(_('current value'), max_digits=12, decimal_places=2, default=0)
    
    # Maintenance
    last_maintenance = models.DateField(_('last maintenance'), null=True, blank=True)
    next_maintenance = models.DateField(_('next maintenance'), null=True, blank=True)
    maintenance_interval_days = models.PositiveIntegerField(_('maintenance interval (days)'), default=365)
    
    is_active = models.BooleanField(_('active'), default=True)
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('asset')
        verbose_name_plural = _('assets')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class MaintenanceLog(models.Model):
    """Log of maintenance work."""
    
    request = models.ForeignKey(MaintenanceRequest, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(_('action'), max_length=200)
    notes = models.TextField(_('notes'), blank=True)
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('maintenance log')
        verbose_name_plural = _('maintenance logs')
        ordering = ['-timestamp']
