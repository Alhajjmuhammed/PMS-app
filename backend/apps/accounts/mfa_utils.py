"""
Multi-Factor Authentication utilities for TOTP, Email, and SMS 2FA.

Uses Django cache (Redis in production) for temporary code storage.
"""
import pyotp
import qrcode
import secrets
import string
from io import BytesIO
from base64 import b64encode
from smtplib import SMTPException
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta


class MFAManager:
    """Manage MFA operations for users."""
    
    @staticmethod
    def generate_totp_secret():
        """Generate a random TOTP secret."""
        return pyotp.random_base32()
    
    @staticmethod
    def get_totp_uri(user, secret=None):
        """
        Generate TOTP provisioning URI for QR code.
        
        Args:
            user: User instance
            secret: TOTP secret (generates new if not provided)
            
        Returns:
            tuple: (secret, provisioning_uri)
        """
        if not secret:
            secret = MFAManager.generate_totp_secret()
        
        totp = pyotp.TOTP(secret)
        issuer_name = getattr(settings, 'MFA_ISSUER_NAME', 'Hotel PMS')
        
        uri = totp.provisioning_uri(
            name=user.email,
            issuer_name=issuer_name
        )
        
        return secret, uri
    
    @staticmethod
    def generate_qr_code(uri):
        """
        Generate QR code image for TOTP setup.
        
        Args:
            uri: TOTP provisioning URI
            
        Returns:
            str: Base64 encoded QR code image
        """
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def verify_totp_code(secret, code):
        """
        Verify TOTP code.
        
        Args:
            secret: User's TOTP secret
            code: 6-digit code from authenticator app
            
        Returns:
            bool: True if valid
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)  # Allow 30s window
    
    @staticmethod
    def generate_backup_codes(count=10):
        """
        Generate backup recovery codes.
        
        Args:
            count: Number of codes to generate
            
        Returns:
            list: List of backup codes
        """
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            codes.append(code)
        return codes
    
    @staticmethod
    def verify_backup_code(user, code):
        """
        Verify and consume a backup code.
        
        Args:
            user: User instance
            code: Backup code to verify
            
        Returns:
            bool: True if valid and consumed
        """
        if not user.mfa_backup_codes:
            return False
        
        # Convert to list if it's a string (JSON field might return string)
        backup_codes = user.mfa_backup_codes if isinstance(user.mfa_backup_codes, list) else []
        
        if code.upper() in backup_codes:
            backup_codes.remove(code.upper())
            user.mfa_backup_codes = backup_codes
            # Note: Caller should save the user model
            return True
        return False
    
    @staticmethod
    def generate_email_code(email):
        """Generate and store email MFA code."""
        return EmailMFA.generate_email_code()
    
    @staticmethod
    def send_email_code(email, code):
        """Send email MFA code."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            return EmailMFA.send_code(user)
        except User.DoesNotExist:
            return False
    
    @staticmethod
    def verify_email_code(email, code):
        """Verify email MFA code."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            return EmailMFA.verify_code(user, code)
        except User.DoesNotExist:
            return False
    
    @staticmethod
    def generate_sms_code(phone):
        """Generate and store SMS MFA code."""
        return SMSMFA.generate_sms_code()
    
    @staticmethod
    def send_sms_code(phone, code):
        """Send SMS MFA code."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(phone=phone)
            return SMSMFA.send_code(user)
        except User.DoesNotExist:
            return False
    
    @staticmethod
    def verify_sms_code(phone, code):
        """Verify SMS MFA code."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(phone=phone)
            return SMSMFA.verify_code(user, code)
        except User.DoesNotExist:
            return False


class EmailMFA:
    """
    Email-based 2FA.
    
    Uses Django cache (Redis in production) for temporary code storage.
    Codes expire after 10 minutes.
    """
    
    CODE_EXPIRY_MINUTES = 10
    
    @staticmethod
    def generate_email_code():
        """Generate 6-digit email code."""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    @staticmethod
    def _get_cache_key(email):
        """Generate cache key for email code."""
        return f"mfa:email:{email}"
    
    @staticmethod
    def send_code(user):
        """
        Send MFA code via email.
        
        Args:
            user: User instance
            
        Returns:
            bool: True if sent successfully
        """
        code = EmailMFA.generate_email_code()
        
        # Store code in cache with 10-minute expiry
        cache_key = EmailMFA._get_cache_key(user.email)
        cache.set(cache_key, code, timeout=EmailMFA.CODE_EXPIRY_MINUTES * 60)
        
        try:
            send_mail(
                subject='Your Login Verification Code',
                message=f'Your verification code is: {code}\n\nThis code will expire in {EmailMFA.CODE_EXPIRY_MINUTES} minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return True
        except (SMTPException, ConnectionError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send email MFA code to user {user.id}: {str(e)}")
            return False
    
    @staticmethod
    def verify_code(user, code):
        """
        Verify email MFA code.
        
        Args:
            user: User instance
            code: 6-digit code
            
        Returns:
            bool: True if valid
        """
        cache_key = EmailMFA._get_cache_key(user.email)
        stored_code = cache.get(cache_key)
        
        if not stored_code:
            return False
        
        # Check code match
        if stored_code == code:
            # Delete code after successful verification (one-time use)
            cache.delete(cache_key)
            return True
        
        return False


class SMSMFA:
    """
    SMS-based 2FA (requires Twilio or similar provider).
    
    Uses Django cache (Redis in production) for temporary code storage.
    Codes expire after 10 minutes.
    """
    
    CODE_EXPIRY_MINUTES = 10
    
    @staticmethod
    def generate_sms_code():
        """Generate 6-digit SMS code."""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    @staticmethod
    def _get_cache_key(phone):
        """Generate cache key for SMS code."""
        return f"mfa:sms:{phone}"
    
    @staticmethod
    def send_code(user):
        """
        Send MFA code via SMS.
        
        Args:
            user: User instance
            
        Returns:
            bool: True if sent successfully
        """
        if not user.phone:
            return False
        
        code = SMSMFA.generate_sms_code()
        
        # Store code in cache with 10-minute expiry
        cache_key = SMSMFA._get_cache_key(user.phone)
        cache.set(cache_key, code, timeout=SMSMFA.CODE_EXPIRY_MINUTES * 60)
        
        # TODO: Integrate with Twilio when credentials available
        # Log SMS attempt without exposing the code (security)
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"SMS verification code sent to user {user.id} (phone: {user.phone[-4:]}***)")
        
        # Uncomment when Twilio is configured:
        # try:
        #     from twilio.rest import Client
        #     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        #     message = client.messages.create(
        #         body=f'Your verification code is: {code}',
        #         from_=settings.TWILIO_PHONE_NUMBER,
        #         to=user.phone
        #     )
        #     return True
        # except Exception as e:
        #     print(f"Failed to send SMS: {e}")
        #     return False
        
        return True  # Development mode always succeeds
    
    @staticmethod
    def verify_code(user, code):
        """
        Verify SMS MFA code.
        
        Args:
            user: User instance
            code: 6-digit code
            
        Returns:
            bool: True if valid
        """
        if not user.phone:
            return False
        
        cache_key = SMSMFA._get_cache_key(user.phone)
        stored_code = cache.get(cache_key)
        
        if not stored_code:
            return False
        
        # Check code match
        if stored_code == code:
            # Delete code after successful verification (one-time use)
            cache.delete(cache_key)
            return True
        
        return False
