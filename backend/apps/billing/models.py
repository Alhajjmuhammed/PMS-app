"""
Billing Models for Hotel PMS
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid


class Folio(models.Model):
    """Guest folio/bill."""
    
    class FolioType(models.TextChoices):
        GUEST = 'GUEST', _('Guest Folio')
        MASTER = 'MASTER', _('Master Folio')
        GROUP = 'GROUP', _('Group Folio')
        COMPANY = 'COMPANY', _('Company Folio')
    
    class Status(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        CLOSED = 'CLOSED', _('Closed')
        SETTLED = 'SETTLED', _('Settled')
    
    folio_number = models.CharField(_('folio number'), max_length=50, unique=True)
    folio_type = models.CharField(_('type'), max_length=20, choices=FolioType.choices, default=FolioType.GUEST)
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.OPEN)
    
    # Links
    reservation = models.OneToOneField('reservations.Reservation', on_delete=models.CASCADE, related_name='folio', null=True, blank=True)
    guest = models.ForeignKey('guests.Guest', on_delete=models.PROTECT, related_name='folios')
    company = models.ForeignKey('guests.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='folios')
    
    # Dates
    open_date = models.DateField(_('open date'), default=timezone.now)
    close_date = models.DateField(_('close date'), null=True, blank=True)
    
    # Amounts
    total_charges = models.DecimalField(_('total charges'), max_digits=12, decimal_places=2, default=0)
    total_payments = models.DecimalField(_('total payments'), max_digits=12, decimal_places=2, default=0)
    total_taxes = models.DecimalField(_('total taxes'), max_digits=12, decimal_places=2, default=0)
    
    # Billing
    billing_address = models.TextField(_('billing address'), blank=True)
    
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('folio')
        verbose_name_plural = _('folios')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.folio_number} - {self.guest}"
    
    @property
    def balance(self):
        return self.total_charges + self.total_taxes - self.total_payments
    
    def recalculate_totals(self):
        self.total_charges = sum(item.amount for item in self.charges.all())
        self.total_payments = sum(payment.amount for payment in self.payments.all())
        self.total_taxes = sum(item.tax_amount for item in self.charges.all())
        self.save()


class ChargeCode(models.Model):
    """Charge codes for billing."""
    
    class ChargeCategory(models.TextChoices):
        ROOM = 'ROOM', _('Room Charge')
        FOOD = 'FOOD', _('Food & Beverage')
        MINIBAR = 'MINIBAR', _('Minibar')
        LAUNDRY = 'LAUNDRY', _('Laundry')
        TELEPHONE = 'TELEPHONE', _('Telephone')
        PARKING = 'PARKING', _('Parking')
        SPA = 'SPA', _('Spa & Wellness')
        OTHER = 'OTHER', _('Other')
    
    code = models.CharField(_('code'), max_length=20, unique=True)
    name = models.CharField(_('name'), max_length=100)
    category = models.CharField(_('category'), max_length=20, choices=ChargeCategory.choices)
    default_amount = models.DecimalField(_('default amount'), max_digits=10, decimal_places=2, default=0)
    is_taxable = models.BooleanField(_('taxable'), default=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('charge code')
        verbose_name_plural = _('charge codes')
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class FolioCharge(models.Model):
    """Individual charges on a folio."""
    
    folio = models.ForeignKey(Folio, on_delete=models.CASCADE, related_name='charges')
    charge_code = models.ForeignKey(ChargeCode, on_delete=models.PROTECT)
    
    description = models.CharField(_('description'), max_length=200)
    quantity = models.DecimalField(_('quantity'), max_digits=8, decimal_places=2, default=1)
    unit_price = models.DecimalField(_('unit price'), max_digits=10, decimal_places=2)
    amount = models.DecimalField(_('amount'), max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(_('tax amount'), max_digits=10, decimal_places=2, default=0)
    
    charge_date = models.DateField(_('charge date'), default=timezone.now)
    reference = models.CharField(_('reference'), max_length=100, blank=True)
    
    is_posted = models.BooleanField(_('posted'), default=True)
    posted_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('folio charge')
        verbose_name_plural = _('folio charges')
        ordering = ['-charge_date', '-posted_at']
    
    def __str__(self):
        return f"{self.folio.folio_number} - {self.description}: {self.amount}"
    
    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.folio.recalculate_totals()


class Payment(models.Model):
    """Payments on a folio."""
    
    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', _('Cash')
        CREDIT_CARD = 'CREDIT_CARD', _('Credit Card')
        DEBIT_CARD = 'DEBIT_CARD', _('Debit Card')
        BANK_TRANSFER = 'BANK_TRANSFER', _('Bank Transfer')
        CITY_LEDGER = 'CITY_LEDGER', _('City Ledger')
        VOUCHER = 'VOUCHER', _('Voucher')
        LOYALTY_POINTS = 'LOYALTY', _('Loyalty Points')
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')
        REFUNDED = 'REFUNDED', _('Refunded')
    
    payment_number = models.CharField(_('payment number'), max_length=50, unique=True)
    folio = models.ForeignKey(Folio, on_delete=models.CASCADE, related_name='payments')
    
    payment_method = models.CharField(_('method'), max_length=20, choices=PaymentMethod.choices)
    amount = models.DecimalField(_('amount'), max_digits=12, decimal_places=2)
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.COMPLETED)
    
    # Card details (for reference)
    card_type = models.CharField(_('card type'), max_length=50, blank=True)
    card_last_four = models.CharField(_('card last 4'), max_length=4, blank=True)
    authorization_code = models.CharField(_('auth code'), max_length=50, blank=True)
    
    reference = models.CharField(_('reference'), max_length=100, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    
    payment_date = models.DateTimeField(_('payment date'), default=timezone.now)
    received_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.payment_number} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_number:
            self.payment_number = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
        self.folio.recalculate_totals()


class Invoice(models.Model):
    """Invoice generation."""
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        ISSUED = 'ISSUED', _('Issued')
        PAID = 'PAID', _('Paid')
        CANCELLED = 'CANCELLED', _('Cancelled')
    
    invoice_number = models.CharField(_('invoice number'), max_length=50, unique=True)
    folio = models.ForeignKey(Folio, on_delete=models.CASCADE, related_name='invoices')
    
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.DRAFT)
    invoice_date = models.DateField(_('invoice date'), default=timezone.now)
    due_date = models.DateField(_('due date'), null=True, blank=True)
    
    # Amounts
    subtotal = models.DecimalField(_('subtotal'), max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(_('tax amount'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=12, decimal_places=2, default=0)
    
    # Billing info
    bill_to_name = models.CharField(_('bill to name'), max_length=200)
    bill_to_address = models.TextField(_('bill to address'), blank=True)
    
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('invoice')
        verbose_name_plural = _('invoices')
        ordering = ['-invoice_date']
    
    def __str__(self):
        return f"{self.invoice_number}"


class CashierShift(models.Model):
    """Cashier shift tracking."""
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='cashier_shifts')
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE)
    
    shift_start = models.DateTimeField(_('shift start'))
    shift_end = models.DateTimeField(_('shift end'), null=True, blank=True)
    
    opening_balance = models.DecimalField(_('opening balance'), max_digits=12, decimal_places=2, default=0)
    closing_balance = models.DecimalField(_('closing balance'), max_digits=12, decimal_places=2, null=True, blank=True)
    
    total_cash_received = models.DecimalField(_('cash received'), max_digits=12, decimal_places=2, default=0)
    total_card_received = models.DecimalField(_('card received'), max_digits=12, decimal_places=2, default=0)
    
    is_balanced = models.BooleanField(_('balanced'), null=True)
    variance = models.DecimalField(_('variance'), max_digits=10, decimal_places=2, default=0)
    
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('cashier shift')
        verbose_name_plural = _('cashier shifts')
        ordering = ['-shift_start']
    
    def __str__(self):
        return f"{self.user} - {self.shift_start.date()}"
