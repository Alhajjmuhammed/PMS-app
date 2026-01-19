from django.contrib import admin
from .models import Season, RatePlan, RoomRate, DateRate, Package, Discount, YieldRule


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'property', 'start_date', 'end_date', 'priority', 'is_active')
    list_filter = ('property', 'is_active')


class RoomRateInline(admin.TabularInline):
    model = RoomRate
    extra = 0


@admin.register(RatePlan)
class RatePlanAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'property', 'rate_type', 'is_refundable', 'is_active')
    list_filter = ('property', 'rate_type', 'is_active')
    search_fields = ('code', 'name')
    inlines = [RoomRateInline]


@admin.register(RoomRate)
class RoomRateAdmin(admin.ModelAdmin):
    list_display = ('rate_plan', 'room_type', 'season', 'single_rate', 'double_rate', 'is_active')
    list_filter = ('rate_plan__property', 'rate_plan', 'is_active')


@admin.register(DateRate)
class DateRateAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'rate_plan', 'date', 'rate', 'is_closed')
    list_filter = ('room_type', 'date')


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'property', 'valid_from', 'valid_to', 'is_active')
    list_filter = ('property', 'is_active')


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'discount_type', 'value', 'times_used', 'max_uses', 'is_active')
    list_filter = ('discount_type', 'is_active')


@admin.register(YieldRule)
class YieldRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'property', 'trigger_type', 'min_threshold', 'adjustment_percent', 'is_active')
    list_filter = ('property', 'trigger_type', 'is_active')
