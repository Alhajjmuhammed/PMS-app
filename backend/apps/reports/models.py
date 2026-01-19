"""
Reports & Analytics Models
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class DailyStatistics(models.Model):
    """Daily property statistics snapshot."""
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='daily_stats')
    date = models.DateField(_('date'))
    
    # Room statistics
    total_rooms = models.PositiveIntegerField(_('total rooms'), default=0)
    rooms_sold = models.PositiveIntegerField(_('rooms sold'), default=0)
    rooms_ooo = models.PositiveIntegerField(_('rooms out of order'), default=0)
    available_rooms = models.PositiveIntegerField(_('available rooms'), default=0)
    complimentary_rooms = models.PositiveIntegerField(_('complimentary rooms'), default=0)
    house_use_rooms = models.PositiveIntegerField(_('house use rooms'), default=0)
    
    # Occupancy
    occupancy_percent = models.DecimalField(_('occupancy %'), max_digits=5, decimal_places=2, default=0)
    
    # Revenue
    room_revenue = models.DecimalField(_('room revenue'), max_digits=12, decimal_places=2, default=0)
    fb_revenue = models.DecimalField(_('F&B revenue'), max_digits=12, decimal_places=2, default=0)
    other_revenue = models.DecimalField(_('other revenue'), max_digits=12, decimal_places=2, default=0)
    total_revenue = models.DecimalField(_('total revenue'), max_digits=12, decimal_places=2, default=0)
    
    # Key metrics
    adr = models.DecimalField(_('ADR'), max_digits=10, decimal_places=2, default=0)  # Average Daily Rate
    revpar = models.DecimalField(_('RevPAR'), max_digits=10, decimal_places=2, default=0)  # Revenue per Available Room
    
    # Guest statistics
    arrivals = models.PositiveIntegerField(_('arrivals'), default=0)
    departures = models.PositiveIntegerField(_('departures'), default=0)
    in_house = models.PositiveIntegerField(_('in house guests'), default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('daily statistics')
        verbose_name_plural = _('daily statistics')
        unique_together = ['property', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.property.name} - {self.date}"


class MonthlyStatistics(models.Model):
    """Monthly property statistics."""
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='monthly_stats')
    year = models.PositiveIntegerField(_('year'))
    month = models.PositiveIntegerField(_('month'))
    
    # Averages
    avg_occupancy = models.DecimalField(_('avg occupancy'), max_digits=5, decimal_places=2, default=0)
    avg_adr = models.DecimalField(_('avg ADR'), max_digits=10, decimal_places=2, default=0)
    avg_revpar = models.DecimalField(_('avg RevPAR'), max_digits=10, decimal_places=2, default=0)
    
    # Totals
    total_room_nights = models.PositiveIntegerField(_('room nights'), default=0)
    total_revenue = models.DecimalField(_('total revenue'), max_digits=12, decimal_places=2, default=0)
    room_revenue = models.DecimalField(_('room revenue'), max_digits=12, decimal_places=2, default=0)
    fb_revenue = models.DecimalField(_('F&B revenue'), max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('monthly statistics')
        verbose_name_plural = _('monthly statistics')
        unique_together = ['property', 'year', 'month']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.property.name} - {self.year}/{self.month}"


class ReportTemplate(models.Model):
    """Saved report template."""
    
    class ReportType(models.TextChoices):
        DAILY = 'DAILY', _('Daily Report')
        OCCUPANCY = 'OCCUPANCY', _('Occupancy Report')
        REVENUE = 'REVENUE', _('Revenue Report')
        ARRIVAL = 'ARRIVAL', _('Arrival Report')
        DEPARTURE = 'DEPARTURE', _('Departure Report')
        IN_HOUSE = 'IN_HOUSE', _('In-House Guest List')
        HOUSEKEEPING = 'HOUSEKEEPING', _('Housekeeping Report')
        RESERVATION = 'RESERVATION', _('Reservation Report')
        PRODUCTION = 'PRODUCTION', _('Production Report')
        AUDIT = 'AUDIT', _('Night Audit Report')
        FORECAST = 'FORECAST', _('Forecast Report')
        CUSTOM = 'CUSTOM', _('Custom Report')
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, null=True, blank=True, related_name='report_templates')
    name = models.CharField(_('name'), max_length=100)
    report_type = models.CharField(_('type'), max_length=20, choices=ReportType.choices)
    description = models.TextField(_('description'), blank=True)
    
    # Report configuration
    config = models.JSONField(_('configuration'), default=dict)
    
    # Scheduling
    is_scheduled = models.BooleanField(_('scheduled'), default=False)
    schedule_time = models.TimeField(_('schedule time'), null=True, blank=True)
    email_recipients = models.TextField(_('email recipients'), blank=True)
    
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('report template')
        verbose_name_plural = _('report templates')
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class NightAudit(models.Model):
    """Night audit record."""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        ROLLED_BACK = 'ROLLED_BACK', _('Rolled Back')
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='night_audits')
    business_date = models.DateField(_('business date'))
    
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Pre-audit checks
    no_shows_processed = models.BooleanField(_('no-shows processed'), default=False)
    room_rates_posted = models.BooleanField(_('room rates posted'), default=False)
    folios_settled = models.BooleanField(_('folios settled'), default=False)
    departures_checked = models.BooleanField(_('departures checked'), default=False)
    
    # Totals
    room_revenue = models.DecimalField(_('room revenue'), max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(_('tax amount'), max_digits=12, decimal_places=2, default=0)
    fb_revenue = models.DecimalField(_('F&B revenue'), max_digits=12, decimal_places=2, default=0)
    other_revenue = models.DecimalField(_('other revenue'), max_digits=12, decimal_places=2, default=0)
    total_revenue = models.DecimalField(_('total revenue'), max_digits=12, decimal_places=2, default=0)
    
    payments_collected = models.DecimalField(_('payments collected'), max_digits=12, decimal_places=2, default=0)
    
    # Room counts
    rooms_sold = models.PositiveIntegerField(_('rooms sold'), default=0)
    arrivals_count = models.PositiveIntegerField(_('arrivals'), default=0)
    departures_count = models.PositiveIntegerField(_('departures'), default=0)
    
    started_at = models.DateTimeField(_('started at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    completed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('night audit')
        verbose_name_plural = _('night audits')
        unique_together = ['property', 'business_date']
        ordering = ['-business_date']
    
    def __str__(self):
        return f"{self.property.name} - {self.business_date}"


class AuditLog(models.Model):
    """Night audit step log."""
    
    night_audit = models.ForeignKey(NightAudit, on_delete=models.CASCADE, related_name='logs')
    step = models.CharField(_('step'), max_length=100)
    message = models.TextField(_('message'))
    is_error = models.BooleanField(_('is error'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('audit log')
        verbose_name_plural = _('audit logs')
        ordering = ['created_at']
