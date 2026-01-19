from django.contrib import admin
from .models import Property, Building, Floor, Department, PropertyAmenity, TaxConfiguration


class BuildingInline(admin.TabularInline):
    model = Building
    extra = 0


class DepartmentInline(admin.TabularInline):
    model = Department
    extra = 0


class PropertyAmenityInline(admin.TabularInline):
    model = PropertyAmenity
    extra = 0


class TaxConfigurationInline(admin.TabularInline):
    model = TaxConfiguration
    extra = 0


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'property_type', 'city', 'country', 'total_rooms', 'is_active')
    list_filter = ('property_type', 'is_active', 'country', 'star_rating')
    search_fields = ('name', 'code', 'city')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'property_type', 'star_rating')
        }),
        ('Contact', {
            'fields': ('email', 'phone', 'fax', 'website')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Settings', {
            'fields': ('total_rooms', 'total_floors', 'check_in_time', 'check_out_time', 'currency', 'timezone', 'tax_id')
        }),
        ('Media', {
            'fields': ('logo', 'image')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    inlines = [BuildingInline, DepartmentInline, PropertyAmenityInline, TaxConfigurationInline]


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'property', 'floors', 'is_active')
    list_filter = ('property', 'is_active')
    search_fields = ('name', 'code')


class FloorInline(admin.TabularInline):
    model = Floor
    extra = 0


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ('building', 'number', 'name')
    list_filter = ('building__property', 'building')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'property', 'manager', 'is_active')
    list_filter = ('property', 'is_active')
    search_fields = ('name', 'code')


@admin.register(PropertyAmenity)
class PropertyAmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'property', 'category', 'is_chargeable', 'price')
    list_filter = ('property', 'category', 'is_chargeable')
    search_fields = ('name',)


@admin.register(TaxConfiguration)
class TaxConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'property', 'rate', 'is_active')
    list_filter = ('property', 'is_active')
    search_fields = ('name', 'code')
