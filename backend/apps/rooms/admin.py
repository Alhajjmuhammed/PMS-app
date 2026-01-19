from django.contrib import admin
from .models import RoomType, RoomAmenity, RoomTypeAmenity, Room, RoomBlock, RoomStatusLog, RoomImage


class RoomTypeAmenityInline(admin.TabularInline):
    model = RoomTypeAmenity
    extra = 1


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'hotel', 'max_occupancy', 'base_rate', 'is_active')
    list_filter = ('hotel', 'is_active')
    search_fields = ('name', 'code')
    inlines = [RoomTypeAmenityInline]


@admin.register(RoomAmenity)
class RoomAmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'code')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'hotel', 'room_type', 'status', 'fo_status', 'is_active')
    list_filter = ('hotel', 'room_type', 'status', 'fo_status', 'is_active')
    search_fields = ('room_number', 'name')
    list_editable = ('status', 'fo_status')


@admin.register(RoomBlock)
class RoomBlockAdmin(admin.ModelAdmin):
    list_display = ('room', 'reason', 'start_date', 'end_date', 'created_by')
    list_filter = ('reason', 'start_date', 'end_date')
    search_fields = ('room__room_number', 'notes')


@admin.register(RoomStatusLog)
class RoomStatusLogAdmin(admin.ModelAdmin):
    list_display = ('room', 'previous_status', 'new_status', 'changed_by', 'timestamp')
    list_filter = ('new_status', 'timestamp')
    search_fields = ('room__room_number',)
    readonly_fields = ('room', 'previous_status', 'new_status', 'changed_by', 'notes', 'timestamp')


@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ('room', 'is_primary', 'sort_order', 'uploaded_at', 'uploaded_by')
    list_filter = ('is_primary', 'uploaded_at')
    search_fields = ('room__room_number', 'caption')
    list_editable = ('is_primary', 'sort_order')
