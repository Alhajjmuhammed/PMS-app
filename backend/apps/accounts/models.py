"""
User and Account Models for Hotel PMS
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager for Hotel PMS."""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model for Hotel PMS."""
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        MANAGER = 'MANAGER', _('Manager')
        FRONT_DESK = 'FRONT_DESK', _('Front Desk')
        HOUSEKEEPING = 'HOUSEKEEPING', _('Housekeeping')
        MAINTENANCE = 'MAINTENANCE', _('Maintenance')
        ACCOUNTANT = 'ACCOUNTANT', _('Accountant')
        POS_STAFF = 'POS_STAFF', _('POS Staff')
        GUEST = 'GUEST', _('Guest')
    
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=Role.choices,
        default=Role.FRONT_DESK
    )
    assigned_property = models.ForeignKey(
        'properties.Property',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name=_('assigned property')
    )
    department = models.ForeignKey(
        'properties.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name=_('department')
    )
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    @property
    def is_manager(self):
        return self.role in [self.Role.ADMIN, self.Role.MANAGER]
    
    @property
    def is_front_desk(self):
        return self.role in [self.Role.ADMIN, self.Role.MANAGER, self.Role.FRONT_DESK]


class StaffProfile(models.Model):
    """Extended profile for staff members."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile'
    )
    employee_id = models.CharField(_('employee ID'), max_length=50, unique=True)
    hire_date = models.DateField(_('hire date'), null=True, blank=True)
    job_title = models.CharField(_('job title'), max_length=100, blank=True)
    emergency_contact = models.CharField(_('emergency contact'), max_length=100, blank=True)
    emergency_phone = models.CharField(_('emergency phone'), max_length=20, blank=True)
    address = models.TextField(_('address'), blank=True)
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('staff profile')
        verbose_name_plural = _('staff profiles')
    
    def __str__(self):
        return f"Profile: {self.user.get_full_name()}"


class ActivityLog(models.Model):
    """Track user activities for audit purposes."""
    
    class ActionType(models.TextChoices):
        LOGIN = 'LOGIN', _('Login')
        LOGOUT = 'LOGOUT', _('Logout')
        CREATE = 'CREATE', _('Create')
        UPDATE = 'UPDATE', _('Update')
        DELETE = 'DELETE', _('Delete')
        VIEW = 'VIEW', _('View')
        PRINT = 'PRINT', _('Print')
        EXPORT = 'EXPORT', _('Export')
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activity_logs'
    )
    action = models.CharField(_('action'), max_length=20, choices=ActionType.choices)
    model_name = models.CharField(_('model name'), max_length=100, blank=True)
    object_id = models.CharField(_('object ID'), max_length=100, blank=True)
    description = models.TextField(_('description'), blank=True)
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('activity log')
        verbose_name_plural = _('activity logs')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"
