"""
Guest Models for Hotel PMS
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Guest(models.Model):
    """Guest profile model."""
    
    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        OTHER = 'O', _('Other')
    
    class GuestType(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', _('Individual')
        CORPORATE = 'CORPORATE', _('Corporate')
        VIP = 'VIP', _('VIP')
        LOYALTY = 'LOYALTY', _('Loyalty Member')
    
    # Basic Info
    title = models.CharField(_('title'), max_length=20, blank=True)
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    middle_name = models.CharField(_('middle name'), max_length=100, blank=True)
    gender = models.CharField(_('gender'), max_length=1, choices=Gender.choices, blank=True)
    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True)
    nationality = models.CharField(_('nationality'), max_length=100, blank=True)
    
    # Contact Info
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('phone'), max_length=20)
    mobile = models.CharField(_('mobile'), max_length=20, blank=True)
    fax = models.CharField(_('fax'), max_length=20, blank=True)
    
    # Address
    address = models.TextField(_('address'), blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    state = models.CharField(_('state'), max_length=100, blank=True)
    country = models.CharField(_('country'), max_length=100, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    
    # ID Documents
    id_type = models.CharField(_('ID type'), max_length=50, blank=True)
    id_number = models.CharField(_('ID number'), max_length=100, blank=True)
    id_expiry = models.DateField(_('ID expiry'), null=True, blank=True)
    id_issuing_country = models.CharField(_('ID issuing country'), max_length=100, blank=True)
    passport_number = models.CharField(_('passport number'), max_length=50, blank=True)
    
    # Guest Type & Company
    guest_type = models.CharField(
        _('guest type'),
        max_length=20,
        choices=GuestType.choices,
        default=GuestType.INDIVIDUAL
    )
    company = models.ForeignKey(
        'Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='guests'
    )
    
    # VIP & Loyalty
    vip_level = models.PositiveSmallIntegerField(_('VIP level'), default=0)
    loyalty_number = models.CharField(_('loyalty number'), max_length=50, blank=True, unique=True, null=True)
    loyalty_tier = models.CharField(_('loyalty tier'), max_length=50, blank=True)
    loyalty_points = models.PositiveIntegerField(_('loyalty points'), default=0)
    
    # Preferences
    language = models.CharField(_('preferred language'), max_length=10, default='en')
    
    # Photo
    photo = models.ImageField(_('photo'), upload_to='guests/', blank=True, null=True)
    
    # Status
    is_blacklisted = models.BooleanField(_('blacklisted'), default=False)
    blacklist_reason = models.TextField(_('blacklist reason'), blank=True)
    
    # Statistics
    total_stays = models.PositiveIntegerField(_('total stays'), default=0)
    total_nights = models.PositiveIntegerField(_('total nights'), default=0)
    total_revenue = models.DecimalField(_('total revenue'), max_digits=12, decimal_places=2, default=0)
    last_stay_date = models.DateField(_('last stay date'), null=True, blank=True)
    
    # Notes
    notes = models.TextField(_('notes'), blank=True)
    
    # Audit
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('guest')
        verbose_name_plural = _('guests')
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['last_name', 'first_name']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        parts = [self.title, self.first_name, self.middle_name, self.last_name]
        return ' '.join(p for p in parts if p)


class GuestPreference(models.Model):
    """Guest preferences."""
    
    class PreferenceCategory(models.TextChoices):
        ROOM = 'ROOM', _('Room')
        PILLOW = 'PILLOW', _('Pillow')
        FOOD = 'FOOD', _('Food')
        BEVERAGE = 'BEVERAGE', _('Beverage')
        NEWSPAPER = 'NEWSPAPER', _('Newspaper')
        OTHER = 'OTHER', _('Other')
    
    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        related_name='preferences'
    )
    category = models.CharField(
        _('category'),
        max_length=20,
        choices=PreferenceCategory.choices,
        default=PreferenceCategory.OTHER
    )
    preference = models.CharField(_('preference'), max_length=200)
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('guest preference')
        verbose_name_plural = _('guest preferences')
    
    def __str__(self):
        return f"{self.guest}: {self.preference}"


class GuestDocument(models.Model):
    """Guest documents."""
    
    class DocumentType(models.TextChoices):
        PASSPORT = 'PASSPORT', _('Passport')
        ID_CARD = 'ID_CARD', _('ID Card')
        DRIVER_LICENSE = 'DRIVER_LICENSE', _('Driver License')
        VISA = 'VISA', _('Visa')
        OTHER = 'OTHER', _('Other')
    
    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(
        _('document type'),
        max_length=20,
        choices=DocumentType.choices
    )
    document_number = models.CharField(_('document number'), max_length=100)
    issuing_country = models.CharField(_('issuing country'), max_length=100, blank=True)
    issue_date = models.DateField(_('issue date'), null=True, blank=True)
    expiry_date = models.DateField(_('expiry date'), null=True, blank=True)
    document_file = models.FileField(_('document file'), upload_to='guest_documents/', blank=True, null=True)
    
    class Meta:
        verbose_name = _('guest document')
        verbose_name_plural = _('guest documents')
        ordering = ['-issue_date']  # Fix: Add default ordering to prevent pagination warning
    
    def __str__(self):
        return f"{self.guest}: {self.document_type}"


class Company(models.Model):
    """Corporate/Travel Agent model."""
    
    class CompanyType(models.TextChoices):
        CORPORATE = 'CORPORATE', _('Corporate')
        TRAVEL_AGENT = 'TRAVEL_AGENT', _('Travel Agent')
        OTA = 'OTA', _('OTA')
        TOUR_OPERATOR = 'TOUR_OPERATOR', _('Tour Operator')
        GOVERNMENT = 'GOVERNMENT', _('Government')
        OTHER = 'OTHER', _('Other')
    
    name = models.CharField(_('company name'), max_length=200)
    code = models.CharField(_('company code'), max_length=20, unique=True)
    company_type = models.CharField(
        _('type'),
        max_length=20,
        choices=CompanyType.choices,
        default=CompanyType.CORPORATE
    )
    
    # Contact
    contact_person = models.CharField(_('contact person'), max_length=100, blank=True)
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    fax = models.CharField(_('fax'), max_length=20, blank=True)
    website = models.URLField(_('website'), blank=True)
    
    # Address
    address = models.TextField(_('address'), blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    country = models.CharField(_('country'), max_length=100, blank=True)
    
    # Financial
    tax_id = models.CharField(_('tax ID'), max_length=50, blank=True)
    credit_limit = models.DecimalField(_('credit limit'), max_digits=12, decimal_places=2, default=0)
    payment_terms = models.PositiveIntegerField(_('payment terms (days)'), default=30)
    discount_percentage = models.DecimalField(_('discount %'), max_digits=5, decimal_places=2, default=0)
    
    # Contract
    contract_start = models.DateField(_('contract start'), null=True, blank=True)
    contract_end = models.DateField(_('contract end'), null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(_('active'), default=True)
    
    # Notes
    notes = models.TextField(_('notes'), blank=True)
    
    # Audit
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('company')
        verbose_name_plural = _('companies')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class LoyaltyProgram(models.Model):
    """Loyalty program configuration."""
    
    property = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='loyalty_programs'
    )
    name = models.CharField(_('program name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    points_per_currency = models.DecimalField(
        _('points per currency unit'),
        max_digits=5,
        decimal_places=2,
        default=1
    )
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('loyalty program')
        verbose_name_plural = _('loyalty programs')
    
    def __str__(self):
        return self.name


class LoyaltyTier(models.Model):
    """Loyalty tier levels."""
    
    program = models.ForeignKey(
        LoyaltyProgram,
        on_delete=models.CASCADE,
        related_name='tiers'
    )
    name = models.CharField(_('tier name'), max_length=50)
    min_points = models.PositiveIntegerField(_('minimum points'))
    benefits = models.TextField(_('benefits'), blank=True)
    discount_percentage = models.DecimalField(_('discount %'), max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = _('loyalty tier')
        verbose_name_plural = _('loyalty tiers')
        ordering = ['min_points']
    
    def __str__(self):
        return f"{self.program.name} - {self.name}"


class LoyaltyTransaction(models.Model):
    """Loyalty points transactions."""
    
    class TransactionType(models.TextChoices):
        EARN = 'EARN', _('Earn')
        REDEEM = 'REDEEM', _('Redeem')
        ADJUST = 'ADJUST', _('Adjustment')
        EXPIRE = 'EXPIRE', _('Expiration')
    
    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        related_name='loyalty_transactions'
    )
    transaction_type = models.CharField(
        _('type'),
        max_length=10,
        choices=TransactionType.choices
    )
    points = models.IntegerField(_('points'))  # Can be negative
    description = models.CharField(_('description'), max_length=200)
    reference = models.CharField(_('reference'), max_length=100, blank=True)
    balance_after = models.PositiveIntegerField(_('balance after'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('loyalty transaction')
        verbose_name_plural = _('loyalty transactions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.guest}: {self.transaction_type} {self.points}"
