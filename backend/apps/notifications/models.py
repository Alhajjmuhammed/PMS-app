"""
Notifications Models
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class NotificationTemplate(models.Model):
    """Notification/email template."""
    
    class TemplateType(models.TextChoices):
        EMAIL = 'EMAIL', _('Email')
        SMS = 'SMS', _('SMS')
        PUSH = 'PUSH', _('Push Notification')
        IN_APP = 'IN_APP', _('In-App')
    
    class TriggerEvent(models.TextChoices):
        RESERVATION_CREATED = 'RESERVATION_CREATED', _('Reservation Created')
        RESERVATION_CONFIRMED = 'RESERVATION_CONFIRMED', _('Reservation Confirmed')
        RESERVATION_CANCELLED = 'RESERVATION_CANCELLED', _('Reservation Cancelled')
        CHECK_IN = 'CHECK_IN', _('Check-In')
        CHECK_OUT = 'CHECK_OUT', _('Check-Out')
        PRE_ARRIVAL = 'PRE_ARRIVAL', _('Pre-Arrival')
        POST_STAY = 'POST_STAY', _('Post-Stay Feedback')
        PAYMENT_RECEIVED = 'PAYMENT_RECEIVED', _('Payment Received')
        INVOICE_GENERATED = 'INVOICE_GENERATED', _('Invoice Generated')
        HOUSEKEEPING_COMPLETE = 'HOUSEKEEPING_COMPLETE', _('Housekeeping Complete')
        MAINTENANCE_ASSIGNED = 'MAINTENANCE_ASSIGNED', _('Maintenance Assigned')
        MAINTENANCE_COMPLETE = 'MAINTENANCE_COMPLETE', _('Maintenance Complete')
        CUSTOM = 'CUSTOM', _('Custom')
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, null=True, blank=True, related_name='notification_templates')
    name = models.CharField(_('name'), max_length=100)
    template_type = models.CharField(_('type'), max_length=20, choices=TemplateType.choices)
    trigger_event = models.CharField(_('trigger event'), max_length=50, choices=TriggerEvent.choices, blank=True)
    
    subject = models.CharField(_('subject'), max_length=255, blank=True)
    body = models.TextField(_('body'))
    
    # For emails
    html_body = models.TextField(_('HTML body'), blank=True)
    
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('notification template')
        verbose_name_plural = _('notification templates')
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class Notification(models.Model):
    """User notification."""
    
    class Priority(models.TextChoices):
        LOW = 'LOW', _('Low')
        NORMAL = 'NORMAL', _('Normal')
        HIGH = 'HIGH', _('High')
        URGENT = 'URGENT', _('Urgent')
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    
    title = models.CharField(_('title'), max_length=255)
    message = models.TextField(_('message'))
    link = models.CharField(_('link'), max_length=255, blank=True)
    
    priority = models.CharField(_('priority'), max_length=20, choices=Priority.choices, default=Priority.NORMAL)
    
    is_read = models.BooleanField(_('read'), default=False)
    read_at = models.DateTimeField(_('read at'), null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"


class EmailLog(models.Model):
    """Email sending log."""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        SENT = 'SENT', _('Sent')
        FAILED = 'FAILED', _('Failed')
        BOUNCED = 'BOUNCED', _('Bounced')
    
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    to_email = models.EmailField(_('to'))
    cc_email = models.EmailField(_('CC'), blank=True)
    subject = models.CharField(_('subject'), max_length=255)
    body = models.TextField(_('body'))
    
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(_('error'), blank=True)
    
    sent_at = models.DateTimeField(_('sent at'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Link to related object
    related_object_type = models.CharField(_('object type'), max_length=50, blank=True)
    related_object_id = models.PositiveIntegerField(_('object ID'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('email log')
        verbose_name_plural = _('email logs')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.to_email} - {self.subject}"


class Alert(models.Model):
    """System alert/notification."""
    
    class AlertType(models.TextChoices):
        INFO = 'INFO', _('Information')
        WARNING = 'WARNING', _('Warning')
        ERROR = 'ERROR', _('Error')
        SUCCESS = 'SUCCESS', _('Success')
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, null=True, blank=True, related_name='alerts')
    
    alert_type = models.CharField(_('type'), max_length=20, choices=AlertType.choices, default=AlertType.INFO)
    title = models.CharField(_('title'), max_length=255)
    message = models.TextField(_('message'))
    
    # Target roles
    target_roles = models.JSONField(_('target roles'), default=list)
    
    is_active = models.BooleanField(_('active'), default=True)
    expires_at = models.DateTimeField(_('expires at'), null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = _('alert')
        verbose_name_plural = _('alerts')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class SMSLog(models.Model):
    """SMS sending log."""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        SENT = 'SENT', _('Sent')
        DELIVERED = 'DELIVERED', _('Delivered')
        FAILED = 'FAILED', _('Failed')
    
    to_number = models.CharField(_('to'), max_length=20)
    message = models.TextField(_('message'))
    
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    provider_message_id = models.CharField(_('message ID'), max_length=100, blank=True)
    error_message = models.TextField(_('error'), blank=True)
    
    sent_at = models.DateTimeField(_('sent at'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('delivered at'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('SMS log')
        verbose_name_plural = _('SMS logs')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.to_number} - {self.status}"


class PushDeviceToken(models.Model):
    """Push notification device token."""
    
    class Platform(models.TextChoices):
        IOS = 'IOS', _('iOS')
        ANDROID = 'ANDROID', _('Android')
        WEB = 'WEB', _('Web')
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='push_devices')
    token = models.CharField(_('device token'), max_length=255, unique=True)
    platform = models.CharField(_('platform'), max_length=20, choices=Platform.choices)
    device_name = models.CharField(_('device name'), max_length=100, blank=True)
    
    is_active = models.BooleanField(_('active'), default=True)
    last_used = models.DateTimeField(_('last used'), auto_now=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('push device token')
        verbose_name_plural = _('push device tokens')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_platform_display()} - {self.token[:20]}..."
