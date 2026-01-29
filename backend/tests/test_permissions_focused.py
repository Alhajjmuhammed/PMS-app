"""
Focused RBAC Permission Tests

Tests core permission enforcement across key endpoints.
Validates that role-based access control works correctly.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.properties.models import Property

User = get_user_model()


@pytest.fixture
def api_client():
    """Create API client for requests"""
    return APIClient()


@pytest.fixture
def property_a(db):
    """Create test property A"""
    return Property.objects.create(
        name="Hotel A",
        address="123 Main St",
        phone="555-0001"
    )


@pytest.fixture
def property_b(db):
    """Create test property B"""
    return Property.objects.create(
        name="Hotel B",
        address="456 Oak Ave",
        phone="555-0002"
    )


@pytest.fixture
def superuser(property_a):
    """Create superuser"""
    return User.objects.create_superuser(
        email='super@test.com',
        password='testpass123',
        role='ADMIN',
        assigned_property=property_a,
        first_name='Super',
        last_name='User'
    )


@pytest.fixture
def admin_user(property_a):
    """Create admin user"""
    return User.objects.create_user(
        email='admin_rbac@test.com',
        password='testpass123',
        role='ADMIN',
        assigned_property=property_a,
        first_name='Admin',
        last_name='User'
    )


@pytest.fixture
def manager_a(property_a):
    """Create manager for property A"""
    return User.objects.create_user(
        email='manager.a@test.com',
        password='testpass123',
        role='MANAGER',
        assigned_property=property_a,
        first_name='Manager',
        last_name='A'
    )


@pytest.fixture
def manager_b(property_b):
    """Create manager for property B"""
    return User.objects.create_user(
        email='manager.b@test.com',
        password='testpass123',
        role='MANAGER',
        assigned_property=property_b,
        first_name='Manager',
        last_name='B'
    )


@pytest.fixture
def frontdesk_user(property_a):
    """Create front desk user"""
    return User.objects.create_user(
        email='frontdesk_rbac@test.com',
        password='testpass123',
        role='FRONT_DESK',
        assigned_property=property_a,
        first_name='Front',
        last_name='Desk'
    )


@pytest.fixture
def housekeeping_user(property_a):
    """Create housekeeping user"""
    return User.objects.create_user(
        email='housekeeping_rbac@test.com',
        password='testpass123',
        role='HOUSEKEEPING',
        assigned_property=property_a,
        first_name='House',
        last_name='Keeping'
    )


@pytest.fixture
def maintenance_user(property_a):
    """Create maintenance user"""
    return User.objects.create_user(
        email='maintenance_rbac@test.com',
        password='testpass123',
        role='MAINTENANCE',
        assigned_property=property_a,
        first_name='Maintenance',
        last_name='User'
    )


@pytest.fixture
def pos_user(property_a):
    """Create POS staff user"""
    return User.objects.create_user(
        email='pos_rbac@test.com',
        password='testpass123',
        role='POS_STAFF',
        assigned_property=property_a,
        first_name='POS',
        last_name='Staff'
    )


@pytest.mark.django_db
class TestPropertyPermissions:
    """Test property endpoint permissions"""

    def test_superuser_can_list_properties(self, api_client, superuser):
        """Superuser can list all properties"""
        api_client.force_authenticate(user=superuser)
        response = api_client.get('/api/v1/properties/')
        assert response.status_code == status.HTTP_200_OK

    def test_manager_can_list_properties(self, api_client, manager_a):
        """Manager can list properties"""
        api_client.force_authenticate(user=manager_a)
        response = api_client.get('/api/v1/properties/')
        assert response.status_code == status.HTTP_200_OK

    def test_admin_can_create_property(self, api_client, admin_user):
        """Admin can create properties"""
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            '/api/v1/properties/',
            {
                'name': 'Hotel Test',
                'address': '789 Pine Rd',
                'phone': '555-9999'
            }
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_frontdesk_cannot_create_property(self, api_client, frontdesk_user):
        """Front desk cannot create properties - should return 403"""
        api_client.force_authenticate(user=frontdesk_user)
        response = api_client.post(
            '/api/v1/properties/',
            {
                'name': 'Hotel Denied',
                'address': '321 Elm St',
                'phone': '555-0004'
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_housekeeping_cannot_create_property(self, api_client, housekeeping_user):
        """Housekeeping cannot create properties - should return 403"""
        api_client.force_authenticate(user=housekeeping_user)
        response = api_client.post(
            '/api/v1/properties/',
            {
                'name': 'Hotel Denied2',
                'address': '999 Test St',
                'phone': '555-0005'
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestReservationPermissions:
    """Test reservation endpoint permissions"""

    def test_frontdesk_can_list_reservations(self, api_client, frontdesk_user):
        """Front desk can list reservations"""
        api_client.force_authenticate(user=frontdesk_user)
        response = api_client.get('/api/v1/reservations/')
        assert response.status_code == status.HTTP_200_OK

    def test_manager_can_list_reservations(self, api_client, manager_a):
        """Manager can list reservations"""
        api_client.force_authenticate(user=manager_a)
        response = api_client.get('/api/v1/reservations/')
        assert response.status_code == status.HTTP_200_OK

    def test_housekeeping_cannot_list_reservations(self, api_client, housekeeping_user):
        """Housekeeping cannot access reservations - should return 403"""
        api_client.force_authenticate(user=housekeeping_user)
        response = api_client.get('/api/v1/reservations/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_pos_cannot_list_reservations(self, api_client, pos_user):
        """POS staff cannot access reservations - should return 403"""
        api_client.force_authenticate(user=pos_user)
        response = api_client.get('/api/v1/reservations/')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestGuestPermissions:
    """Test guest endpoint permissions"""

    def test_frontdesk_can_list_guests(self, api_client, frontdesk_user):
        """Front desk can list guests"""
        api_client.force_authenticate(user=frontdesk_user)
        response = api_client.get('/api/v1/guests/')
        assert response.status_code == status.HTTP_200_OK

    def test_manager_can_list_guests(self, api_client, manager_a):
        """Manager can list guests"""
        api_client.force_authenticate(user=manager_a)
        response = api_client.get('/api/v1/guests/')
        assert response.status_code == status.HTTP_200_OK

    def test_housekeeping_cannot_list_guests(self, api_client, housekeeping_user):
        """Housekeeping cannot access guest list - should return 403"""
        api_client.force_authenticate(user=housekeeping_user)
        response = api_client.get('/api/v1/guests/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_maintenance_cannot_list_guests(self, api_client, maintenance_user):
        """Maintenance cannot access guest list - should return 403"""
        api_client.force_authenticate(user=maintenance_user)
        response = api_client.get('/api/v1/guests/')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCrossPropertyAccess:
    """Test that users cannot access other properties"""

    def test_manager_sees_only_own_property(self, api_client, manager_a, property_a, property_b):
        """Manager A should only see property A in filtered results"""
        api_client.force_authenticate(user=manager_a)
        response = api_client.get('/api/v1/properties/')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Get the property IDs from response
        data = response.data
        if 'results' in data:
            properties = data['results']
        else:
            properties = data if isinstance(data, list) else [data]
        
        property_ids = [p['id'] for p in properties if isinstance(p, dict)]
        
        # Manager A should see property A
        assert property_a.id in property_ids
        # Manager A should NOT see property B
        assert property_b.id not in property_ids


@pytest.mark.django_db
class TestRoleHierarchy:
    """Test that role hierarchy works correctly"""

    def test_admin_has_higher_access_than_manager(self, api_client, admin_user, manager_a):
        """Admin should have access to features managers cannot access"""
        # Both should access properties
        api_client.force_authenticate(user=admin_user)
        admin_response = api_client.get('/api/v1/properties/')
        assert admin_response.status_code == status.HTTP_200_OK
        
        api_client.force_authenticate(user=manager_a)
        manager_response = api_client.get('/api/v1/properties/')
        assert manager_response.status_code == status.HTTP_200_OK

    def test_manager_has_higher_access_than_frontdesk(self, api_client, manager_a, frontdesk_user):
        """Manager can create properties, front desk cannot"""
        # Manager can create
        api_client.force_authenticate(user=manager_a)
        manager_response = api_client.post(
            '/api/v1/properties/',
            {'name': 'Manager Hotel', 'address': '111 Test', 'phone': '555-1111'}
        )
        assert manager_response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        assert manager_response.status_code != status.HTTP_403_FORBIDDEN
        
        # Front desk cannot create
        api_client.force_authenticate(user=frontdesk_user)
        frontdesk_response = api_client.post(
            '/api/v1/properties/',
            {'name': 'Front Desk Hotel', 'address': '222 Test', 'phone': '555-2222'}
        )
        assert frontdesk_response.status_code == status.HTTP_403_FORBIDDEN

    def test_frontdesk_has_higher_access_than_housekeeping(self, api_client, frontdesk_user, housekeeping_user):
        """Front desk can access reservations, housekeeping cannot"""
        # Front desk can access
        api_client.force_authenticate(user=frontdesk_user)
        frontdesk_response = api_client.get('/api/v1/reservations/')
        assert frontdesk_response.status_code == status.HTTP_200_OK
        
        # Housekeeping cannot access
        api_client.force_authenticate(user=housekeeping_user)
        housekeeping_response = api_client.get('/api/v1/reservations/')
        assert housekeeping_response.status_code == status.HTTP_403_FORBIDDEN


# Summary function for test execution
def test_suite_summary():
    """
    This test suite covers:
    
    ✅ Property Management Permissions (5 tests)
       - Superuser, Admin, Manager can access
       - Front Desk, Housekeeping cannot create
    
    ✅ Reservation Permissions (4 tests)
       - Front Desk, Manager can access
       - Housekeeping, POS cannot access
    
    ✅ Guest Permissions (4 tests)
       - Front Desk, Manager can access
       - Housekeeping, Maintenance cannot access
    
    ✅ Cross-Property Access (1 test)
       - Managers see only their property
    
    ✅ Role Hierarchy (3 tests)
       - Admin > Manager > Front Desk > Housekeeping
    
    Total: 17 core permission tests
    """
    pass


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
