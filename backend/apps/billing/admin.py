from django.contrib import admin
from .models import Folio, ChargeCode, FolioCharge, Payment, Invoice, CashierShift


class FolioChargeInline(admin.TabularInline):
    model = FolioCharge
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Folio)
class FolioAdmin(admin.ModelAdmin):
    list_display = ('folio_number', 'guest', 'folio_type', 'status', 'total_charges', 'total_payments', 'balance')
    list_filter = ('status', 'folio_type')
    search_fields = ('folio_number', 'guest__first_name', 'guest__last_name')
    inlines = [FolioChargeInline, PaymentInline]


@admin.register(ChargeCode)
class ChargeCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'default_amount', 'is_taxable', 'is_active')
    list_filter = ('category', 'is_active')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_number', 'folio', 'payment_method', 'amount', 'status', 'payment_date')
    list_filter = ('payment_method', 'status', 'payment_date')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'folio', 'status', 'total', 'invoice_date')
    list_filter = ('status', 'invoice_date')


@admin.register(CashierShift)
class CashierShiftAdmin(admin.ModelAdmin):
    list_display = ('user', 'shift_start', 'shift_end', 'opening_balance', 'closing_balance', 'is_balanced')
    list_filter = ('is_balanced', 'shift_start')
