"""
Custom throttling classes for rate limiting sensitive operations.
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class WebhookThrottle(AnonRateThrottle):
    """
    Throttle for webhook endpoints to prevent abuse.
    Allows 60 webhook requests per minute per IP address.
    """
    scope = 'webhook'
    rate = '60/minute'
    
    def get_cache_key(self, request, view):
        """
        Use IP + property_channel_id for rate limiting.
        This prevents one malicious actor from exhausting limits for all channels.
        """
        # Get property_channel_id from URL kwargs
        property_channel_id = view.kwargs.get('property_channel_id', 'unknown')
        ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': f"{ident}:{property_channel_id}"
        }


class MFAVerifyThrottle(AnonRateThrottle):
    """
    Strict throttle for MFA verification to prevent brute force attacks.
    Allows only 5 attempts per minute per user/IP.
    """
    scope = 'mfa_verify'
    rate = '5/minute'
    
    def get_cache_key(self, request, view):
        """
        Rate limit by IP address only. Never trust client-supplied identifiers.
        """
        ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class MFASendThrottle(UserRateThrottle):
    """
    Throttle for sending MFA codes (email/SMS).
    Prevents spam and SMS bombing attacks.
    Allows 3 requests per minute per user.
    """
    scope = 'mfa_send'
    rate = '3/minute'


class LoginThrottle(AnonRateThrottle):
    """
    Throttle for login attempts to prevent brute force attacks.
    Allows 10 login attempts per hour per IP.
    """
    scope = 'login'
    rate = '10/hour'
