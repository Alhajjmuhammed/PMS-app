"""
Tests for Notifications Module
"""

import pytest
from datetime import datetime, timedelta
from django.utils import timezone

from apps.notifications.models import (
    NotificationTemplate, Notification, EmailLog, Alert, SMSLog
)
from apps.properties.models import Property
from apps.accounts.models import User


@pytest.fixture
def setup_notifications_data(db):
    """Setup test data for notifications tests."""
    # Create property
    property = Property.objects.create(
        name='Seaside Hotel',
        code='SEASIDE',
        address='Ocean Blvd',
        city='Los Angeles',
        country='USA',
        email='info@seasidehotel.com',
        phone='+1234567890'
    )
    
    # Create users
    user1 = User.objects.create_user(
        email='manager@seasidehotel.com',
        password='testpass123',
        first_name='Hotel',
        last_name='Manager',
        role='MANAGER'
    )
    
    user2 = User.objects.create_user(
        email='staff@seasidehotel.com',
        password='testpass123',
        first_name='Front',
        last_name='Desk',
        role='STAFF'
    )
    
    return {
        'property': property,
        'user1': user1,
        'user2': user2
    }


@pytest.mark.django_db
class TestNotificationsModels:
    """Test Notifications module models."""
    
    def test_create_notification_template(self, setup_notifications_data):
        """Test creating notification template."""
        template = NotificationTemplate.objects.create(
            property=setup_notifications_data['property'],
            name='Reservation Confirmation',
            template_type='EMAIL',
            trigger_event='RESERVATION_CONFIRMED',
            subject='Your Reservation is Confirmed - {reservation_id}',
            body='Dear {guest_name}, Your reservation for {check_in_date} to {check_out_date} is confirmed.',
            html_body='<h1>Reservation Confirmed</h1><p>Dear {guest_name},</p>',
            is_active=True
        )
        
        assert template.id is not None
        assert template.template_type == 'EMAIL'
        assert template.trigger_event == 'RESERVATION_CONFIRMED'
        assert '{guest_name}' in template.body
    
    def test_notification_template_types(self, setup_notifications_data):
        """Test different notification template types."""
        email = NotificationTemplate.objects.create(
            name='Email Template',
            template_type='EMAIL',
            body='Email content'
        )
        
        sms = NotificationTemplate.objects.create(
            name='SMS Template',
            template_type='SMS',
            body='SMS content'
        )
        
        push = NotificationTemplate.objects.create(
            name='Push Template',
            template_type='PUSH',
            body='Push notification content'
        )
        
        assert email.template_type == 'EMAIL'
        assert sms.template_type == 'SMS'
        assert push.template_type == 'PUSH'
    
    def test_notification_template_trigger_events(self, setup_notifications_data):
        """Test various trigger events."""
        pre_arrival = NotificationTemplate.objects.create(
            name='Pre-Arrival Message',
            template_type='EMAIL',
            trigger_event='PRE_ARRIVAL',
            subject='Arriving Soon?',
            body='We look forward to your arrival tomorrow!'
        )
        
        post_stay = NotificationTemplate.objects.create(
            name='Post-Stay Feedback',
            template_type='EMAIL',
            trigger_event='POST_STAY',
            subject='How was your stay?',
            body='Please share your feedback'
        )
        
        assert pre_arrival.trigger_event == 'PRE_ARRIVAL'
        assert post_stay.trigger_event == 'POST_STAY'
    
    def test_create_user_notification(self, setup_notifications_data):
        """Test creating user notification."""
        notification = Notification.objects.create(
            user=setup_notifications_data['user1'],
            title='New Reservation',
            message='A new reservation has been received for tomorrow',
            link='/reservations/12345',
            priority='NORMAL',
            is_read=False
        )
        
        assert notification.id is not None
        assert notification.is_read is False
        assert notification.priority == 'NORMAL'
        assert notification.user == setup_notifications_data['user1']
    
    def test_notification_priorities(self, setup_notifications_data):
        """Test different notification priorities."""
        low = Notification.objects.create(
            user=setup_notifications_data['user1'],
            title='Info',
            message='FYI',
            priority='LOW'
        )
        
        urgent = Notification.objects.create(
            user=setup_notifications_data['user1'],
            title='Emergency',
            message='System failure',
            priority='URGENT'
        )
        
        assert low.priority == 'LOW'
        assert urgent.priority == 'URGENT'
    
    def test_mark_notification_as_read(self, setup_notifications_data):
        """Test marking notification as read."""
        notification = Notification.objects.create(
            user=setup_notifications_data['user2'],
            title='Reminder',
            message='Check-out reminder',
            is_read=False
        )
        
        assert notification.is_read is False
        assert notification.read_at is None
        
        # Mark as read
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        assert notification.is_read is True
        assert notification.read_at is not None
    
    def test_unread_notifications_filter(self, setup_notifications_data):
        """Test filtering unread notifications."""
        Notification.objects.create(
            user=setup_notifications_data['user1'],
            title='Unread 1',
            message='Message 1',
            is_read=False
        )
        
        Notification.objects.create(
            user=setup_notifications_data['user1'],
            title='Read',
            message='Message 2',
            is_read=True
        )
        
        Notification.objects.create(
            user=setup_notifications_data['user1'],
            title='Unread 2',
            message='Message 3',
            is_read=False
        )
        
        unread = Notification.objects.filter(
            user=setup_notifications_data['user1'],
            is_read=False
        ).count()
        
        assert unread == 2
    
    def test_create_email_log(self, setup_notifications_data):
        """Test creating email log entry."""
        template = NotificationTemplate.objects.create(
            name='Confirmation Email',
            template_type='EMAIL',
            body='Template body'
        )
        
        email = EmailLog.objects.create(
            template=template,
            to_email='guest@example.com',
            cc_email='manager@seasidehotel.com',
            subject='Booking Confirmation',
            body='Your booking is confirmed',
            status='PENDING',
            related_object_type='reservation',
            related_object_id=12345
        )
        
        assert email.id is not None
        assert email.status == 'PENDING'
        assert email.related_object_id == 12345
    
    def test_email_log_statuses(self, setup_notifications_data):
        """Test email log different statuses."""
        pending = EmailLog.objects.create(
            to_email='test1@example.com',
            subject='Test 1',
            body='Body 1',
            status='PENDING'
        )
        
        sent = EmailLog.objects.create(
            to_email='test2@example.com',
            subject='Test 2',
            body='Body 2',
            status='SENT',
            sent_at=timezone.now()
        )
        
        failed = EmailLog.objects.create(
            to_email='test3@example.com',
            subject='Test 3',
            body='Body 3',
            status='FAILED',
            error_message='SMTP connection error'
        )
        
        assert pending.status == 'PENDING'
        assert sent.status == 'SENT'
        assert sent.sent_at is not None
        assert failed.status == 'FAILED'
        assert 'error' in failed.error_message
    
    def test_email_log_lifecycle(self, setup_notifications_data):
        """Test email log from pending to sent."""
        email = EmailLog.objects.create(
            to_email='customer@example.com',
            subject='Welcome',
            body='Welcome to our hotel',
            status='PENDING'
        )
        
        assert email.status == 'PENDING'
        assert email.sent_at is None
        
        # Send email
        email.status = 'SENT'
        email.sent_at = timezone.now()
        email.save()
        
        assert email.status == 'SENT'
        assert email.sent_at is not None
    
    def test_create_alert(self, setup_notifications_data):
        """Test creating system alert."""
        alert = Alert.objects.create(
            property=setup_notifications_data['property'],
            alert_type='WARNING',
            title='System Maintenance Scheduled',
            message='System will be down for maintenance on Sunday',
            target_roles=['MANAGER', 'STAFF'],
            is_active=True,
            expires_at=timezone.now() + timedelta(days=7),
            created_by=setup_notifications_data['user1']
        )
        
        assert alert.id is not None
        assert alert.alert_type == 'WARNING'
        assert 'MANAGER' in alert.target_roles
        assert alert.is_active is True
    
    def test_alert_types(self, setup_notifications_data):
        """Test different alert types."""
        info = Alert.objects.create(
            title='Info Alert',
            message='Information message',
            alert_type='INFO'
        )
        
        warning = Alert.objects.create(
            title='Warning Alert',
            message='Warning message',
            alert_type='WARNING'
        )
        
        error = Alert.objects.create(
            title='Error Alert',
            message='Error message',
            alert_type='ERROR'
        )
        
        success = Alert.objects.create(
            title='Success Alert',
            message='Success message',
            alert_type='SUCCESS'
        )
        
        assert info.alert_type == 'INFO'
        assert warning.alert_type == 'WARNING'
        assert error.alert_type == 'ERROR'
        assert success.alert_type == 'SUCCESS'
    
    def test_alert_with_expiration(self, setup_notifications_data):
        """Test alert expiration."""
        alert = Alert.objects.create(
            title='Limited Time Offer',
            message='Special discount available',
            alert_type='INFO',
            is_active=True,
            expires_at=timezone.now() + timedelta(days=1)
        )
        
        assert alert.is_active is True
        assert alert.expires_at is not None
        
        # Simulate expiration
        alert.is_active = False
        alert.save()
        
        assert alert.is_active is False
    
    def test_alert_target_roles(self, setup_notifications_data):
        """Test alert role targeting."""
        manager_alert = Alert.objects.create(
            property=setup_notifications_data['property'],
            title='Manager Only',
            message='For managers only',
            alert_type='INFO',
            target_roles=['MANAGER'],
            created_by=setup_notifications_data['user1']
        )
        
        staff_alert = Alert.objects.create(
            property=setup_notifications_data['property'],
            title='Staff Alert',
            message='For all staff',
            alert_type='INFO',
            target_roles=['MANAGER', 'STAFF', 'HOUSEKEEPER'],
            created_by=setup_notifications_data['user1']
        )
        
        assert manager_alert.target_roles == ['MANAGER']
        assert len(staff_alert.target_roles) == 3
    
    def test_create_sms_log(self, setup_notifications_data):
        """Test creating SMS log entry."""
        sms = SMSLog.objects.create(
            to_number='+1234567890',
            message='Your reservation is confirmed. Ref: ABC123',
            status='PENDING'
        )
        
        assert sms.id is not None
        assert sms.status == 'PENDING'
        assert sms.to_number == '+1234567890'
    
    def test_sms_log_statuses(self, setup_notifications_data):
        """Test SMS log different statuses."""
        pending = SMSLog.objects.create(
            to_number='+1111111111',
            message='Pending message',
            status='PENDING'
        )
        
        sent = SMSLog.objects.create(
            to_number='+2222222222',
            message='Sent message',
            status='SENT',
            sent_at=timezone.now(),
            provider_message_id='MSG-12345'
        )
        
        delivered = SMSLog.objects.create(
            to_number='+3333333333',
            message='Delivered message',
            status='DELIVERED',
            sent_at=timezone.now(),
            delivered_at=timezone.now(),
            provider_message_id='MSG-67890'
        )
        
        failed = SMSLog.objects.create(
            to_number='+4444444444',
            message='Failed message',
            status='FAILED',
            error_message='Invalid phone number'
        )
        
        assert pending.status == 'PENDING'
        assert sent.status == 'SENT'
        assert sent.provider_message_id == 'MSG-12345'
        assert delivered.status == 'DELIVERED'
        assert delivered.delivered_at is not None
        assert failed.status == 'FAILED'
        assert failed.error_message is not None
    
    def test_sms_log_lifecycle(self, setup_notifications_data):
        """Test SMS log from pending to delivered."""
        sms = SMSLog.objects.create(
            to_number='+1234567890',
            message='Test message',
            status='PENDING'
        )
        
        assert sms.status == 'PENDING'
        assert sms.sent_at is None
        
        # Mark as sent
        sms.status = 'SENT'
        sms.sent_at = timezone.now()
        sms.provider_message_id = 'MSG-ABC123'
        sms.save()
        
        assert sms.status == 'SENT'
        assert sms.sent_at is not None
        
        # Mark as delivered
        sms.status = 'DELIVERED'
        sms.delivered_at = timezone.now()
        sms.save()
        
        assert sms.status == 'DELIVERED'
        assert sms.delivered_at is not None
    
    def test_multiple_notifications_per_user(self, setup_notifications_data):
        """Test multiple notifications for same user."""
        Notification.objects.create(
            user=setup_notifications_data['user1'],
            title='Notification 1',
            message='Message 1'
        )
        
        Notification.objects.create(
            user=setup_notifications_data['user1'],
            title='Notification 2',
            message='Message 2'
        )
        
        Notification.objects.create(
            user=setup_notifications_data['user1'],
            title='Notification 3',
            message='Message 3'
        )
        
        count = Notification.objects.filter(
            user=setup_notifications_data['user1']
        ).count()
        
        assert count == 3
    
    def test_notification_template_without_property(self, setup_notifications_data):
        """Test global notification template."""
        template = NotificationTemplate.objects.create(
            property=None,  # Global template
            name='Global Welcome Email',
            template_type='EMAIL',
            subject='Welcome',
            body='Welcome message'
        )
        
        assert template.id is not None
        assert template.property is None
    
    def test_email_bounced_status(self, setup_notifications_data):
        """Test email bounced status."""
        email = EmailLog.objects.create(
            to_email='invalid@invalid.invalid',
            subject='Test',
            body='Test body',
            status='SENT',
            sent_at=timezone.now()
        )
        
        # Simulate bounce
        email.status = 'BOUNCED'
        email.error_message = 'Email address does not exist'
        email.save()
        
        assert email.status == 'BOUNCED'
        assert 'not exist' in email.error_message
