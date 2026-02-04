"""
Custom authentication classes for token expiration.
"""

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from django.conf import settings
from datetime import timedelta


class ExpiringTokenAuthentication(TokenAuthentication):
    """
    Token authentication with expiration.
    Tokens expire after configured hours of inactivity (default: 24 hours).
    This is a "sliding window" expiration - token is refreshed on each request.
    
    NOTE: Set TOKEN_EXPIRATION_HOURS=0 in settings to disable expiration.
    """
    
    def authenticate_credentials(self, key):
        model = self.get_model()
        
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted.')

        # Get token expiration hours from settings (default: 24, 0 = disabled)
        expiration_hours = getattr(settings, 'TOKEN_EXPIRATION_HOURS', 24)
        
        # If expiration is disabled (0), skip expiration check
        if expiration_hours > 0:
            # Check if token.created is valid (not None)
            if token.created is None:
                # Old token without timestamp - refresh it instead of rejecting
                token.created = timezone.now()
                token.save(update_fields=['created'])
            else:
                expiration_time = token.created + timedelta(hours=expiration_hours)
                
                if timezone.now() > expiration_time:
                    # Token has expired, delete it
                    token.delete()
                    raise AuthenticationFailed('Token has expired. Please login again.')

                # Update token created time to extend session (sliding window)
                # Only update every 5 minutes to reduce DB writes
                time_since_created = timezone.now() - token.created
                if time_since_created.total_seconds() > 300:  # 5 minutes
                    token.created = timezone.now()
                    token.save(update_fields=['created'])

        return (token.user, token)
