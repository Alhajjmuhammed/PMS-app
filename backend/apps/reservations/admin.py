from django.contrib import admin
from .models import Reservation, ReservationRoom, ReservationRateDetail, GroupBooking, ReservationLog


class ReservationRoomInline(admin.TabularInline):
    model = ReservationRoom
    extra = 1


class ReservationLogInline(admin.TabularInline):
    model = ReservationLog
    extra = 0
    readonly_fields = ('action', 'old_value', 'new_value', 'notes', 'user', 'timestamp')
    can_delete = False


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'confirmation_number', 'guest', 'hotel', 'check_in_date', 
        'check_out_date', 'status', 'source', 'total_amount', 'created_at'
    )
    list_filter = ('status', 'source', 'hotel', 'check_in_date')
    search_fields = ('confirmation_number', 'guest__first_name', 'guest__last_name', 'external_id')
    date_hierarchy = 'check_in_date'
    readonly_fields = ('confirmation_number', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Reservation Info', {
            'fields': ('confirmation_number', 'external_id', 'hotel', 'status', 'source')
        }),
        ('Guest Info', {
            'fields': ('guest', 'company', 'adults', 'children', 'infants')
        }),
        ('Dates', {
            'fields': ('check_in_date', 'check_out_date', 'arrival_time', 'departure_time')
        }),
        ('Financial', {
            'fields': ('rate_plan', 'total_amount', 'deposit_amount', 'deposit_paid')
        }),
        ('Notes', {
            'fields': ('special_requests', 'internal_notes')
        }),
        ('Group & Channel', {
            'fields': ('group', 'channel')
        }),
        ('Audit', {
            'fields': ('created_by', 'modified_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ReservationRoomInline, ReservationLogInline]


@admin.register(ReservationRoom)
class ReservationRoomAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'room_type', 'room', 'rate_per_night', 'total_rate')
    list_filter = ('room_type', 'reservation__hotel')
    search_fields = ('reservation__confirmation_number', 'room__room_number')


@admin.register(GroupBooking)
class GroupBookingAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name', 'hotel', 'check_in_date', 'check_out_date',
        'rooms_blocked', 'rooms_picked_up', 'status'
    )
    list_filter = ('status', 'hotel', 'check_in_date')
    search_fields = ('code', 'name', 'contact_name')
    date_hierarchy = 'check_in_date'


@admin.register(ReservationLog)
class ReservationLogAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'action', 'user', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('reservation__confirmation_number',)
    readonly_fields = ('reservation', 'action', 'old_value', 'new_value', 'notes', 'user', 'timestamp')
