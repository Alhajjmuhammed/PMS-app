from django.contrib import admin
from .models import (
    Channel, PropertyChannel, RoomTypeMapping, RatePlanMapping,
    AvailabilityUpdate, RateUpdate, ChannelReservation
)


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'channel_type', 'commission_percent', 'is_active')
    list_filter = ('channel_type', 'is_active')


class RoomTypeMappingInline(admin.TabularInline):
    model = RoomTypeMapping
    extra = 0


class RatePlanMappingInline(admin.TabularInline):
    model = RatePlanMapping
    extra = 0


@admin.register(PropertyChannel)
class PropertyChannelAdmin(admin.ModelAdmin):
    list_display = ('property', 'channel', 'property_code', 'last_sync', 'is_active')
    list_filter = ('channel', 'is_active')
    inlines = [RoomTypeMappingInline, RatePlanMappingInline]


@admin.register(AvailabilityUpdate)
class AvailabilityUpdateAdmin(admin.ModelAdmin):
    list_display = ('property_channel', 'room_type', 'date', 'availability', 'status', 'created_at')
    list_filter = ('status', 'property_channel__channel')


@admin.register(RateUpdate)
class RateUpdateAdmin(admin.ModelAdmin):
    list_display = ('property_channel', 'room_type', 'rate_plan', 'date', 'rate', 'status')
    list_filter = ('status', 'property_channel__channel')


@admin.register(ChannelReservation)
class ChannelReservationAdmin(admin.ModelAdmin):
    list_display = ('channel_booking_id', 'property_channel', 'guest_name', 'check_in_date', 'status', 'received_at')
    list_filter = ('status', 'property_channel__channel')
    search_fields = ('channel_booking_id', 'guest_name')
