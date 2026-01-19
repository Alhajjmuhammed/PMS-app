"""
POS Models for Hotel PMS
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid


class Outlet(models.Model):
    """Restaurant/Bar outlet."""
    
    class OutletType(models.TextChoices):
        RESTAURANT = 'RESTAURANT', _('Restaurant')
        BAR = 'BAR', _('Bar')
        CAFE = 'CAFE', _('Cafe')
        ROOM_SERVICE = 'ROOM_SERVICE', _('Room Service')
        SPA = 'SPA', _('Spa')
        POOL = 'POOL', _('Pool Bar')
        OTHER = 'OTHER', _('Other')
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='outlets')
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=20)
    outlet_type = models.CharField(_('type'), max_length=20, choices=OutletType.choices)
    
    location = models.CharField(_('location'), max_length=200, blank=True)
    capacity = models.PositiveIntegerField(_('capacity'), default=0)
    
    opening_time = models.TimeField(_('opening time'), null=True, blank=True)
    closing_time = models.TimeField(_('closing time'), null=True, blank=True)
    
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('outlet')
        verbose_name_plural = _('outlets')
        unique_together = ['property', 'code']
    
    def __str__(self):
        return f"{self.property.name} - {self.name}"


class MenuCategory(models.Model):
    """Menu category."""
    
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    sort_order = models.PositiveIntegerField(_('sort order'), default=0)
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('menu category')
        verbose_name_plural = _('menu categories')
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return f"{self.outlet.name} - {self.name}"


class MenuItem(models.Model):
    """Menu item."""
    
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    cost = models.DecimalField(_('cost'), max_digits=10, decimal_places=2, default=0)
    
    is_available = models.BooleanField(_('available'), default=True)
    is_taxable = models.BooleanField(_('taxable'), default=True)
    
    image = models.ImageField(_('image'), upload_to='menu_items/', blank=True, null=True)
    
    class Meta:
        verbose_name = _('menu item')
        verbose_name_plural = _('menu items')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.price}"


class POSOrder(models.Model):
    """POS order."""
    
    class Status(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        CLOSED = 'CLOSED', _('Closed')
        VOIDED = 'VOIDED', _('Voided')
    
    order_number = models.CharField(_('order number'), max_length=50, unique=True)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE, related_name='orders')
    
    # Guest link
    check_in = models.ForeignKey('frontdesk.CheckIn', on_delete=models.SET_NULL, null=True, blank=True, related_name='pos_orders')
    room_number = models.CharField(_('room number'), max_length=20, blank=True)
    guest_name = models.CharField(_('guest name'), max_length=200, blank=True)
    
    # Table (for restaurant)
    table_number = models.CharField(_('table number'), max_length=20, blank=True)
    covers = models.PositiveIntegerField(_('covers'), default=1)
    
    # Amounts
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(_('tax'), max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(_('discount'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.OPEN)
    
    # Post to room
    is_posted_to_room = models.BooleanField(_('posted to room'), default=False)
    posted_at = models.DateTimeField(_('posted at'), null=True, blank=True)
    
    notes = models.TextField(_('notes'), blank=True)
    server = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='pos_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('POS order')
        verbose_name_plural = _('POS orders')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"POS-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class POSOrderItem(models.Model):
    """POS order item."""
    
    order = models.ForeignKey(POSOrder, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    
    quantity = models.PositiveIntegerField(_('quantity'), default=1)
    unit_price = models.DecimalField(_('unit price'), max_digits=10, decimal_places=2)
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    
    notes = models.CharField(_('notes'), max_length=200, blank=True)
    is_voided = models.BooleanField(_('voided'), default=False)
    
    class Meta:
        verbose_name = _('POS order item')
        verbose_name_plural = _('POS order items')
    
    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
