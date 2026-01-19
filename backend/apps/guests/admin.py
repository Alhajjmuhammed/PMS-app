from django.contrib import admin
from .models import Guest, GuestPreference, GuestDocument, Company, LoyaltyProgram, LoyaltyTier, LoyaltyTransaction


class GuestPreferenceInline(admin.TabularInline):
    model = GuestPreference
    extra = 0


class GuestDocumentInline(admin.TabularInline):
    model = GuestDocument
    extra = 0


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'guest_type', 'vip_level', 'total_stays')
    list_filter = ('guest_type', 'vip_level', 'is_blacklisted', 'nationality')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'id_number', 'passport_number')
    inlines = [GuestPreferenceInline, GuestDocumentInline]
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('title', 'first_name', 'middle_name', 'last_name', 'gender', 'date_of_birth', 'nationality', 'photo')
        }),
        ('Contact', {
            'fields': ('email', 'phone', 'mobile', 'fax')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Identification', {
            'fields': ('id_type', 'id_number', 'id_expiry', 'id_issuing_country', 'passport_number')
        }),
        ('Guest Type & Company', {
            'fields': ('guest_type', 'company', 'vip_level')
        }),
        ('Loyalty', {
            'fields': ('loyalty_number', 'loyalty_tier', 'loyalty_points')
        }),
        ('Statistics', {
            'fields': ('total_stays', 'total_nights', 'total_revenue', 'last_stay_date'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_blacklisted', 'blacklist_reason', 'notes')
        }),
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'company_type', 'contact_person', 'is_active')
    list_filter = ('company_type', 'is_active')
    search_fields = ('name', 'code', 'contact_person', 'email')


class LoyaltyTierInline(admin.TabularInline):
    model = LoyaltyTier
    extra = 0


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'property', 'points_per_currency', 'is_active')
    list_filter = ('property', 'is_active')
    inlines = [LoyaltyTierInline]


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ('guest', 'transaction_type', 'points', 'balance_after', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('guest__first_name', 'guest__last_name', 'description')
    readonly_fields = ('guest', 'transaction_type', 'points', 'description', 'reference', 'balance_after', 'created_at')
