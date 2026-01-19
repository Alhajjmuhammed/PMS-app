from django.contrib import admin
from .models import Outlet, MenuCategory, MenuItem, POSOrder, POSOrderItem


@admin.register(Outlet)
class OutletAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'property', 'outlet_type', 'is_active')
    list_filter = ('property', 'outlet_type', 'is_active')


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'outlet', 'sort_order', 'is_active')
    list_filter = ('outlet', 'is_active')


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available')
    list_filter = ('category__outlet', 'is_available')
    search_fields = ('name',)


class POSOrderItemInline(admin.TabularInline):
    model = POSOrderItem
    extra = 0


@admin.register(POSOrder)
class POSOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'outlet', 'room_number', 'total', 'status', 'is_posted_to_room', 'created_at')
    list_filter = ('outlet', 'status', 'is_posted_to_room')
    search_fields = ('order_number', 'room_number', 'guest_name')
    inlines = [POSOrderItemInline]
