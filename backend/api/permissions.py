"""
Custom permission classes for role-based access control.
"""
from rest_framework.permissions import BasePermission


class IsSuperuser(BasePermission):
    """
    Permission class that allows access only to superusers.
    Used for: Properties, Users, System Settings
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsAdminOrManager(BasePermission):
    """
    Permission class that allows access to Admin and Manager roles.
    Used for: Property management, Staff management
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role in ['ADMIN', 'MANAGER']


class IsFrontDeskOrAbove(BasePermission):
    """
    Permission class for Front Desk staff and above.
    Used for: Reservations, Guest management, Check-in/out
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        allowed_roles = ['ADMIN', 'MANAGER', 'FRONT_DESK']
        return request.user.is_superuser or request.user.role in allowed_roles


class IsHousekeepingStaff(BasePermission):
    """
    Permission class for Housekeeping staff.
    Used for: Housekeeping tasks, Room status updates
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        allowed_roles = ['ADMIN', 'MANAGER', 'HOUSEKEEPING']
        return request.user.is_superuser or request.user.role in allowed_roles


class IsMaintenanceStaff(BasePermission):
    """
    Permission class for Maintenance staff.
    Used for: Maintenance requests, Work orders
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        allowed_roles = ['ADMIN', 'MANAGER', 'MAINTENANCE']
        return request.user.is_superuser or request.user.role in allowed_roles


class IsAccountantOrAbove(BasePermission):
    """
    Permission class for Accountants and above.
    Used for: Financial reports, Billing, Revenue data
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        allowed_roles = ['ADMIN', 'MANAGER', 'ACCOUNTANT']
        return request.user.is_superuser or request.user.role in allowed_roles


class IsPOSStaff(BasePermission):
    """
    Permission class for POS staff.
    Used for: POS operations, Menu management, Order processing
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        allowed_roles = ['ADMIN', 'MANAGER', 'POS_STAFF']
        return request.user.is_superuser or request.user.role in allowed_roles


class IsGuest(BasePermission):
    """
    Permission class for Guest users.
    Used for: Guest portal, View own reservations, Own bills
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'GUEST'


class CanViewInvoices(BasePermission):
    """
    Permission class for viewing invoices.
    Front Desk can view invoices for check-out, but not full billing access.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        allowed_roles = ['ADMIN', 'MANAGER', 'ACCOUNTANT', 'FRONT_DESK']
        # Front desk can only read invoices, not create/modify
        if request.user.role == 'FRONT_DESK':
            return request.method in ['GET', 'HEAD', 'OPTIONS']
        return request.user.is_superuser or request.user.role in allowed_roles
        if not request.user or not request.user.is_authenticated:
            return False
        allowed_roles = ['ADMIN', 'MANAGER', 'POS_STAFF']
        return request.user.is_superuser or request.user.role in allowed_roles


class IsReadOnly(BasePermission):
    """
    Permission class that allows read-only access.
    Allows: GET, HEAD, OPTIONS
    Denies: POST, PUT, PATCH, DELETE
    """
    def has_permission(self, request, view):
        return request.method in ['GET', 'HEAD', 'OPTIONS']


class CanManageUsers(BasePermission):
    """
    Permission class for user management.
    Only superusers can manage users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class CanManageProperties(BasePermission):
    """
    Permission class for property management.
    Only superusers can create/delete properties.
    Managers can view and update their own property.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers can do everything
        if request.user.is_superuser:
            return True
        
        # Managers can only view (GET requests)
        if request.user.role == 'MANAGER' and request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        return False
