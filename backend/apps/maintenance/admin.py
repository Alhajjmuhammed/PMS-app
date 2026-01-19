from django.contrib import admin
from .models import MaintenanceRequest, Asset, MaintenanceLog


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('request_number', 'title', 'request_type', 'priority', 'status', 'assigned_to', 'created_at')
    list_filter = ('status', 'request_type', 'priority', 'property')
    search_fields = ('request_number', 'title', 'description')
    list_editable = ('status', 'assigned_to')


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'location', 'is_active')
    list_filter = ('category', 'property', 'is_active')
    search_fields = ('code', 'name', 'serial_number')


@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ('request', 'action', 'user', 'timestamp')
    list_filter = ('timestamp',)
