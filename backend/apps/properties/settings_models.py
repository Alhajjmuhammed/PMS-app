"""
System Settings Models
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class SystemSetting(models.Model):
    """System-wide or property-specific settings."""
    
    property = models.OneToOneField(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='settings',
        null=True,
        blank=True,
        help_text=_('Leave blank for system-wide settings')
    )
    
    # Regional Settings
    language = models.CharField(_('language'), max_length=10, default='en')
    timezone = models.CharField(_('timezone'), max_length=50, default='UTC')
    currency = models.CharField(_('currency'), max_length=3, default='USD')
    date_format = models.CharField(_('date format'), max_length=20, default='YYYY-MM-DD')
    time_format = models.CharField(_('time format'), max_length=20, default='HH:mm')
    
    # Appearance
    theme = models.CharField(_('theme'), max_length=20, default='light', choices=[
        ('light', _('Light')),
        ('dark', _('Dark')),
        ('auto', _('Auto'))
    ])
    
    # Notification Preferences
    email_notifications = models.BooleanField(_('email notifications'), default=True)
    push_notifications = models.BooleanField(_('push notifications'), default=True)
    sms_notifications = models.BooleanField(_('SMS notifications'), default=False)
    
    # Business Settings
    tax_rate = models.DecimalField(_('tax rate'), max_digits=5, decimal_places=2, default=0)
    service_charge_rate = models.DecimalField(_('service charge rate'), max_digits=5, decimal_places=2, default=0)
    
    # Check-in/Check-out
    check_in_time = models.TimeField(_('check-in time'), default='14:00')
    check_out_time = models.TimeField(_('check-out time'), default='11:00')
    
    # Additional settings stored as JSON
    extra_settings = models.JSONField(_('extra settings'), default=dict, blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('system setting')
        verbose_name_plural = _('system settings')
    
    def __str__(self):
        if self.property:
            return f"Settings for {self.property.name}"
        return "Global System Settings"
