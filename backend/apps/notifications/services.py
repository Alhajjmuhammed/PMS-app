"""
Notification Services
Handles push notifications, email, and SMS
"""

import logging
from typing import List, Dict, Any, Optional
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class PushNotificationService:
    """Service for sending push notifications via Firebase Cloud Messaging"""
    
    def __init__(self):
        self.enabled = getattr(settings, 'FCM_ENABLED', False)
        self.server_key = getattr(settings, 'FCM_SERVER_KEY', None)
        self.api_url = 'https://fcm.googleapis.com/fcm/send'
    
    def send_notification(
        self,
        device_tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send push notification to devices
        
        Args:
            device_tokens: List of FCM device tokens
            title: Notification title
            body: Notification body
            data: Optional custom data payload
        """
        if not self.enabled:
            logger.warning("Push notifications are disabled")
            return {'success': False, 'error': 'Push notifications disabled'}
        
        if not self.server_key:
            logger.error("FCM server key not configured")
            return {'success': False, 'error': 'FCM not configured'}
        
        try:
            import requests
            
            headers = {
                'Authorization': f'key={self.server_key}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'registration_ids': device_tokens,
                'notification': {
                    'title': title,
                    'body': body,
                    'sound': 'default',
                },
                'data': data or {},
                'priority': 'high',
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Push notification sent: {result.get('success', 0)} successful")
                return {
                    'success': True,
                    'results': result
                }
            else:
                logger.error(f"FCM error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_to_user(
        self,
        user,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send notification to a specific user
        Looks up user's device tokens from their profile
        """
        # Get user's device tokens (would need to be stored in user profile)
        device_tokens = getattr(user, 'fcm_tokens', [])
        
        if not device_tokens:
            logger.warning(f"User {user.id} has no FCM tokens")
            return {'success': False, 'error': 'No device tokens'}
        
        return self.send_notification(device_tokens, title, body, data)


class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.enabled = getattr(settings, 'EMAIL_ENABLED', True)
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        message: str,
        html_message: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send email
        
        Args:
            to_emails: List of recipient emails
            subject: Email subject
            message: Plain text message
            html_message: Optional HTML version
            cc: Optional CC recipients
            bcc: Optional BCC recipients
        """
        if not self.enabled:
            logger.warning("Email is disabled")
            return False
        
        try:
            if html_message:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=self.from_email,
                    to=to_emails,
                    cc=cc,
                    bcc=bcc
                )
                email.attach_alternative(html_message, "text/html")
                email.send()
            else:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=self.from_email,
                    recipient_list=to_emails,
                    fail_silently=False
                )
            
            logger.info(f"Email sent to {', '.join(to_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_reservation_confirmation(self, reservation) -> bool:
        """Send reservation confirmation email"""
        subject = f"Reservation Confirmation - {reservation.property.name}"
        
        context = {
            'reservation': reservation,
            'guest': reservation.guest,
            'property': reservation.property,
        }
        
        message = f"""
Dear {reservation.guest.first_name},

Your reservation has been confirmed!

Confirmation Code: {reservation.confirmation_code}
Check-in: {reservation.check_in_date}
Check-out: {reservation.check_out_date}
Guests: {reservation.adults} adults, {reservation.children} children

Property: {reservation.property.name}
Address: {reservation.property.address}

Thank you for choosing us!
        """.strip()
        
        # Could use a template here
        html_message = f"""
<html>
<body>
    <h2>Reservation Confirmed</h2>
    <p>Dear {reservation.guest.first_name},</p>
    <p>Your reservation has been confirmed!</p>
    
    <h3>Reservation Details</h3>
    <ul>
        <li><strong>Confirmation Code:</strong> {reservation.confirmation_code}</li>
        <li><strong>Check-in:</strong> {reservation.check_in_date}</li>
        <li><strong>Check-out:</strong> {reservation.check_out_date}</li>
        <li><strong>Guests:</strong> {reservation.adults} adults, {reservation.children} children</li>
    </ul>
    
    <h3>Property Information</h3>
    <p><strong>{reservation.property.name}</strong><br>
    {reservation.property.address}</p>
    
    <p>Thank you for choosing us!</p>
</body>
</html>
        """
        
        return self.send_email(
            to_emails=[reservation.guest.email],
            subject=subject,
            message=message,
            html_message=html_message
        )
    
    def send_check_in_reminder(self, reservation) -> bool:
        """Send check-in reminder email"""
        subject = f"Check-in Reminder - {reservation.property.name}"
        
        message = f"""
Dear {reservation.guest.first_name},

This is a reminder that your check-in is tomorrow!

Confirmation Code: {reservation.confirmation_code}
Check-in Date: {reservation.check_in_date}
Check-in Time: {reservation.property.check_in_time}

We look forward to welcoming you!
        """.strip()
        
        return self.send_email(
            to_emails=[reservation.guest.email],
            subject=subject,
            message=message
        )


class SMSService:
    """Service for sending SMS via Twilio"""
    
    def __init__(self):
        self.enabled = getattr(settings, 'SMS_ENABLED', False)
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        self.from_number = getattr(settings, 'TWILIO_FROM_NUMBER', None)
    
    def send_sms(self, to_number: str, message: str) -> bool:
        """
        Send SMS message
        
        Args:
            to_number: Recipient phone number (E.164 format)
            message: SMS message text
        """
        if not self.enabled:
            logger.warning("SMS is disabled")
            return False
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.error("Twilio credentials not configured")
            return False
        
        try:
            from twilio.rest import Client
            
            client = Client(self.account_sid, self.auth_token)
            
            message = client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            logger.info(f"SMS sent to {to_number}: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return False
    
    def send_reservation_confirmation_sms(self, reservation) -> bool:
        """Send reservation confirmation via SMS"""
        if not reservation.guest.phone:
            return False
        
        message = f"""
{reservation.property.name} - Reservation Confirmed!
Code: {reservation.confirmation_code}
Check-in: {reservation.check_in_date}
        """.strip()
        
        return self.send_sms(reservation.guest.phone, message)


# Service instances
push_service = PushNotificationService()
email_service = EmailService()
sms_service = SMSService()


# Convenience functions
def send_push_notification(device_tokens: List[str], title: str, body: str, data: Optional[Dict] = None):
    """Send push notification"""
    return push_service.send_notification(device_tokens, title, body, data)


def send_email(to_emails: List[str], subject: str, message: str, html_message: Optional[str] = None):
    """Send email"""
    return email_service.send_email(to_emails, subject, message, html_message)


def send_sms(to_number: str, message: str):
    """Send SMS"""
    return sms_service.send_sms(to_number, message)
