from django.contrib import admin
from .models import CheckIn, CheckOut, RoomMove, WalkIn, GuestMessage


class RoomMoveInline(admin.TabularInline):
    model = RoomMove
    extra = 0


class GuestMessageInline(admin.TabularInline):
    model = GuestMessage
    extra = 0


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'guest', 'room', 'check_in_time', 'expected_check_out')
    list_filter = ('check_in_time', 'room__hotel')
    search_fields = ('registration_number', 'guest__first_name', 'guest__last_name')
    date_hierarchy = 'check_in_time'
    inlines = [RoomMoveInline, GuestMessageInline]


@admin.register(CheckOut)
class CheckOutAdmin(admin.ModelAdmin):
    list_display = ('check_in', 'check_out_time', 'total_charges', 'total_payments', 'balance')
    list_filter = ('check_out_time', 'is_express')
    search_fields = ('check_in__registration_number', 'check_in__guest__first_name')
    date_hierarchy = 'check_out_time'


@admin.register(RoomMove)
class RoomMoveAdmin(admin.ModelAdmin):
    list_display = ('check_in', 'from_room', 'to_room', 'move_time', 'reason')
    list_filter = ('move_time',)
    search_fields = ('check_in__registration_number', 'reason')


@admin.register(WalkIn)
class WalkInAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'room_type', 'check_in_date', 'is_converted')
    list_filter = ('property', 'is_converted', 'check_in_date')
    search_fields = ('first_name', 'last_name', 'email', 'phone')


@admin.register(GuestMessage)
class GuestMessageAdmin(admin.ModelAdmin):
    list_display = ('check_in', 'message_type', 'from_name', 'is_delivered', 'created_at')
    list_filter = ('message_type', 'is_delivered')
    search_fields = ('check_in__guest__first_name', 'message')
