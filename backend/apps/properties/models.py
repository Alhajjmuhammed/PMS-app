"""
Property and Hotel Models for Hotel PMS
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Property(models.Model):
    """Hotel/Property model."""
    
    class PropertyType(models.TextChoices):
        HOTEL = 'HOTEL', _('Hotel')
        RESORT = 'RESORT', _('Resort')
        MOTEL = 'MOTEL', _('Motel')
        HOSTEL = 'HOSTEL', _('Hostel')
        APARTMENT = 'APARTMENT', _('Apartment')
        VILLA = 'VILLA', _('Villa')
        GUESTHOUSE = 'GUESTHOUSE', _('Guest House')
    
    name = models.CharField(_('property name'), max_length=200)
    code = models.CharField(_('property code'), max_length=20, unique=True)
    property_type = models.CharField(
        _('property type'),
        max_length=20,
        choices=PropertyType.choices,
        default=PropertyType.HOTEL
    )
    
    # Contact Information
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    fax = models.CharField(_('fax'), max_length=20, blank=True)
    website = models.URLField(_('website'), blank=True)
    
    # Address
    address = models.TextField(_('address'))
    city = models.CharField(_('city'), max_length=100)
    state = models.CharField(_('state/province'), max_length=100, blank=True)
    country = models.CharField(_('country'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    
    # Details
    star_rating = models.PositiveSmallIntegerField(_('star rating'), default=3)
    total_rooms = models.PositiveIntegerField(_('total rooms'), default=0)
    total_floors = models.PositiveIntegerField(_('total floors'), default=1)
    check_in_time = models.TimeField(_('check-in time'), default='14:00')
    check_out_time = models.TimeField(_('check-out time'), default='12:00')
    
    # Taxes and Settings
    tax_id = models.CharField(_('tax ID'), max_length=50, blank=True)
    currency = models.CharField(_('currency'), max_length=3, default='USD')
    timezone = models.CharField(_('timezone'), max_length=50, default='UTC')
    
    # Images
    logo = models.ImageField(_('logo'), upload_to='properties/logos/', blank=True, null=True)
    image = models.ImageField(_('main image'), upload_to='properties/images/', blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('property')
        verbose_name_plural = _('properties')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Building(models.Model):
    """Building within a property."""
    
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='buildings'
    )
    name = models.CharField(_('building name'), max_length=100)
    code = models.CharField(_('building code'), max_length=20)
    floors = models.PositiveIntegerField(_('number of floors'), default=1)
    description = models.TextField(_('description'), blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('building')
        verbose_name_plural = _('buildings')
        unique_together = ['property', 'code']
        ordering = ['property', 'name']
    
    def __str__(self):
        return f"{self.property.name} - {self.name}"


class Floor(models.Model):
    """Floor within a building."""
    
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name='building_floors'
    )
    number = models.IntegerField(_('floor number'))
    name = models.CharField(_('floor name'), max_length=50, blank=True)
    description = models.TextField(_('description'), blank=True)
    
    class Meta:
        verbose_name = _('floor')
        verbose_name_plural = _('floors')
        unique_together = ['building', 'number']
        ordering = ['building', 'number']
    
    def __str__(self):
        return f"{self.building.name} - Floor {self.number}"


class Department(models.Model):
    """Department within a property."""
    
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='departments'
    )
    name = models.CharField(_('department name'), max_length=100)
    code = models.CharField(_('department code'), max_length=20)
    description = models.TextField(_('description'), blank=True)
    manager = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments'
    )
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('department')
        verbose_name_plural = _('departments')
        unique_together = ['property', 'code']
        ordering = ['property', 'name']
    
    def __str__(self):
        return f"{self.property.name} - {self.name}"


class PropertyAmenity(models.Model):
    """Amenities available at property level."""
    
    class AmenityCategory(models.TextChoices):
        GENERAL = 'GENERAL', _('General')
        SERVICES = 'SERVICES', _('Services')
        DINING = 'DINING', _('Dining')
        RECREATION = 'RECREATION', _('Recreation')
        BUSINESS = 'BUSINESS', _('Business')
        WELLNESS = 'WELLNESS', _('Wellness')
        ACCESSIBILITY = 'ACCESSIBILITY', _('Accessibility')
    
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='amenities'
    )
    name = models.CharField(_('amenity name'), max_length=100)
    category = models.CharField(
        _('category'),
        max_length=20,
        choices=AmenityCategory.choices,
        default=AmenityCategory.GENERAL
    )
    description = models.TextField(_('description'), blank=True)
    icon = models.CharField(_('icon'), max_length=50, blank=True)
    is_chargeable = models.BooleanField(_('chargeable'), default=False)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = _('property amenity')
        verbose_name_plural = _('property amenities')
        ordering = ['property', 'category', 'name']
    
    def __str__(self):
        return f"{self.property.name} - {self.name}"


class TaxConfiguration(models.Model):
    """Tax settings for a property."""
    
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='taxes'
    )
    name = models.CharField(_('tax name'), max_length=100)
    code = models.CharField(_('tax code'), max_length=20)
    rate = models.DecimalField(_('rate (%)'), max_digits=5, decimal_places=2)
    is_percentage = models.BooleanField(_('is percentage'), default=True)
    applies_to_room = models.BooleanField(_('applies to room'), default=True)
    applies_to_services = models.BooleanField(_('applies to services'), default=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('tax configuration')
        verbose_name_plural = _('tax configurations')
        unique_together = ['property', 'code']
    
    def __str__(self):
        return f"{self.property.name} - {self.name} ({self.rate}%)"
