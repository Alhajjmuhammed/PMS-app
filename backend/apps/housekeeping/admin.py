from django.contrib import admin
from .models import HousekeepingTask, RoomInspection, LinenInventory, AmenityInventory, HousekeepingSchedule


@admin.register(HousekeepingTask)
class HousekeepingTaskAdmin(admin.ModelAdmin):
    list_display = ('room', 'task_type', 'priority', 'status', 'assigned_to', 'scheduled_date')
    list_filter = ('status', 'task_type', 'priority', 'scheduled_date')
    search_fields = ('room__room_number', 'notes')
    list_editable = ('status', 'assigned_to')
    date_hierarchy = 'scheduled_date'


@admin.register(RoomInspection)
class RoomInspectionAdmin(admin.ModelAdmin):
    list_display = ('room', 'inspector', 'inspection_date', 'overall_score', 'passed')
    list_filter = ('passed', 'inspection_date')
    search_fields = ('room__room_number',)


@admin.register(LinenInventory)
class LinenInventoryAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'linen_type', 'quantity_total', 'quantity_in_use', 'quantity_available')
    list_filter = ('hotel', 'linen_type')


@admin.register(AmenityInventory)
class AmenityInventoryAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'name', 'code', 'quantity', 'reorder_level')
    list_filter = ('hotel', 'category')
    search_fields = ('name', 'code')


@admin.register(HousekeepingSchedule)
class HousekeepingScheduleAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'shift_start', 'shift_end', 'assigned_floor')
    list_filter = ('date', 'assigned_floor')
    search_fields = ('user__first_name', 'user__last_name')
