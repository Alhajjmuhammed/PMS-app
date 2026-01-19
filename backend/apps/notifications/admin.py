from django.contrib import admin
from .models import NotificationTemplate, Notification, EmailLog, Alert, SMSLog


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'trigger_event', 'is_active')
    list_filter = ('template_type', 'trigger_event', 'is_active')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'priority', 'is_read', 'created_at')
    list_filter = ('priority', 'is_read')


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('to_email', 'subject', 'status', 'sent_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('to_email', 'subject')


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'alert_type', 'property', 'is_active', 'expires_at')
    list_filter = ('alert_type', 'is_active')


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('to_number', 'status', 'sent_at', 'created_at')
    list_filter = ('status',)
