"""
Rate & Revenue Management Models
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Season(models.Model):
    """Pricing season."""
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='seasons')
    name = models.CharField(_('name'), max_length=100)
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    
    priority = models.PositiveIntegerField(_('priority'), default=0, help_text="Higher priority overrides lower")
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('season')
        verbose_name_plural = _('seasons')
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"


class RatePlan(models.Model):
    """Rate plan."""
    
    class RateType(models.TextChoices):
        RACK = 'RACK', _('Rack Rate')
        BAR = 'BAR', _('Best Available Rate')
        CORPORATE = 'CORPORATE', _('Corporate Rate')
        GOVERNMENT = 'GOVERNMENT', _('Government Rate')
        AAA = 'AAA', _('AAA Rate')
        SENIOR = 'SENIOR', _('Senior Rate')
        PACKAGE = 'PACKAGE', _('Package Rate')
        PROMOTIONAL = 'PROMOTIONAL', _('Promotional Rate')
        OTA = 'OTA', _('OTA Rate')
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='rate_plans')
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=20)
    rate_type = models.CharField(_('type'), max_length=20, choices=RateType.choices, default=RateType.BAR)
    description = models.TextField(_('description'), blank=True)
    
    # Booking restrictions
    min_nights = models.PositiveIntegerField(_('minimum nights'), default=1)
    max_nights = models.PositiveIntegerField(_('maximum nights'), null=True, blank=True)
    min_advance_booking = models.PositiveIntegerField(_('min advance days'), default=0)
    max_advance_booking = models.PositiveIntegerField(_('max advance days'), null=True, blank=True)
    
    # Cancellation
    cancellation_policy = models.TextField(_('cancellation policy'), blank=True)
    cancellation_hours = models.PositiveIntegerField(_('cancellation hours'), default=24)
    
    # Validity
    valid_from = models.DateField(_('valid from'), null=True, blank=True)
    valid_to = models.DateField(_('valid to'), null=True, blank=True)
    
    is_refundable = models.BooleanField(_('refundable'), default=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('rate plan')
        verbose_name_plural = _('rate plans')
        unique_together = ['property', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class RoomRate(models.Model):
    """Room rate per room type and rate plan."""
    
    rate_plan = models.ForeignKey(RatePlan, on_delete=models.CASCADE, related_name='room_rates')
    room_type = models.ForeignKey('rooms.RoomType', on_delete=models.CASCADE, related_name='rates')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=True, blank=True)
    
    # Occupancy-based pricing
    single_rate = models.DecimalField(_('single rate'), max_digits=10, decimal_places=2)
    double_rate = models.DecimalField(_('double rate'), max_digits=10, decimal_places=2)
    extra_adult = models.DecimalField(_('extra adult'), max_digits=10, decimal_places=2, default=0)
    extra_child = models.DecimalField(_('extra child'), max_digits=10, decimal_places=2, default=0)
    
    # Day-of-week rates (optional)
    sunday_rate = models.DecimalField(_('Sunday'), max_digits=10, decimal_places=2, null=True, blank=True)
    monday_rate = models.DecimalField(_('Monday'), max_digits=10, decimal_places=2, null=True, blank=True)
    tuesday_rate = models.DecimalField(_('Tuesday'), max_digits=10, decimal_places=2, null=True, blank=True)
    wednesday_rate = models.DecimalField(_('Wednesday'), max_digits=10, decimal_places=2, null=True, blank=True)
    thursday_rate = models.DecimalField(_('Thursday'), max_digits=10, decimal_places=2, null=True, blank=True)
    friday_rate = models.DecimalField(_('Friday'), max_digits=10, decimal_places=2, null=True, blank=True)
    saturday_rate = models.DecimalField(_('Saturday'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('room rate')
        verbose_name_plural = _('room rates')
        unique_together = ['rate_plan', 'room_type', 'season']
    
    def __str__(self):
        return f"{self.rate_plan.code} - {self.room_type.code}"


class DateRate(models.Model):
    """Override rate for specific date."""
    
    room_type = models.ForeignKey('rooms.RoomType', on_delete=models.CASCADE, related_name='date_rates')
    rate_plan = models.ForeignKey(RatePlan, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(_('date'))
    rate = models.DecimalField(_('rate'), max_digits=10, decimal_places=2)
    
    min_stay = models.PositiveIntegerField(_('minimum stay'), null=True, blank=True)
    is_closed = models.BooleanField(_('closed for sale'), default=False)
    
    class Meta:
        verbose_name = _('date rate')
        verbose_name_plural = _('date rates')
        unique_together = ['room_type', 'rate_plan', 'date']
    
    def __str__(self):
        return f"{self.room_type.code} - {self.date} - {self.rate}"


class Package(models.Model):
    """Package/promotional bundle."""
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='packages')
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=20)
    description = models.TextField(_('description'))
    
    rate_plan = models.ForeignKey(RatePlan, on_delete=models.CASCADE, related_name='packages')
    
    # Package inclusions
    includes_breakfast = models.BooleanField(_('includes breakfast'), default=False)
    includes_dinner = models.BooleanField(_('includes dinner'), default=False)
    includes_spa = models.BooleanField(_('includes spa'), default=False)
    other_inclusions = models.TextField(_('other inclusions'), blank=True)
    
    # Pricing
    package_price = models.DecimalField(_('package price'), max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percent = models.DecimalField(_('discount %'), max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Validity
    valid_from = models.DateField(_('valid from'))
    valid_to = models.DateField(_('valid to'))
    
    min_nights = models.PositiveIntegerField(_('minimum nights'), default=1)
    
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('package')
        verbose_name_plural = _('packages')
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Discount(models.Model):
    """Discount codes."""
    
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'PERCENTAGE', _('Percentage')
        FIXED = 'FIXED', _('Fixed Amount')
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='discounts')
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=50, unique=True)
    
    discount_type = models.CharField(_('type'), max_length=20, choices=DiscountType.choices)
    value = models.DecimalField(_('value'), max_digits=10, decimal_places=2)
    
    # Restrictions
    valid_from = models.DateField(_('valid from'))
    valid_to = models.DateField(_('valid to'))
    max_uses = models.PositiveIntegerField(_('max uses'), null=True, blank=True)
    times_used = models.PositiveIntegerField(_('times used'), default=0)
    
    min_nights = models.PositiveIntegerField(_('min nights'), null=True, blank=True)
    min_amount = models.DecimalField(_('min amount'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('discount')
        verbose_name_plural = _('discounts')
    
    def __str__(self):
        return f"{self.code} - {self.value}{'%' if self.discount_type == 'PERCENTAGE' else ''}"


class YieldRule(models.Model):
    """Dynamic pricing rules."""
    
    class TriggerType(models.TextChoices):
        OCCUPANCY = 'OCCUPANCY', _('Occupancy Based')
        DAY_AHEAD = 'DAY_AHEAD', _('Days Ahead')
        DEMAND = 'DEMAND', _('Demand Based')
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='yield_rules')
    name = models.CharField(_('name'), max_length=100)
    
    trigger_type = models.CharField(_('trigger'), max_length=20, choices=TriggerType.choices)
    
    # Thresholds
    min_threshold = models.PositiveIntegerField(_('min threshold'))
    max_threshold = models.PositiveIntegerField(_('max threshold'), null=True, blank=True)
    
    # Adjustment
    adjustment_percent = models.DecimalField(_('adjustment %'), max_digits=5, decimal_places=2)
    
    priority = models.PositiveIntegerField(_('priority'), default=0)
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('yield rule')
        verbose_name_plural = _('yield rules')
        ordering = ['-priority']
    
    def __str__(self):
        return f"{self.name} - {self.adjustment_percent}%"
