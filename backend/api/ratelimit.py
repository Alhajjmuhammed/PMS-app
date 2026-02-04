"""
Rate limiting decorators and utilities for API endpoints.
"""

from django_ratelimit.decorators import ratelimit
from functools import wraps
from django.http import JsonResponse


def api_ratelimit(key='ip', rate='60/m', method=['GET', 'POST', 'PUT', 'PATCH', 'DELETE']):
    """
    Decorator for rate limiting API endpoints.
    
    Usage:
        @api_ratelimit(key='ip', rate='60/m')
        class MyAPIView(APIView):
            ...
    
    Args:
        key: What to use for rate limiting (ip, user, or user_or_ip)
        rate: Rate limit string (e.g., '60/m', '100/h', '1000/d')
        method: HTTP methods to rate limit
    """
    def decorator(view_func):
        @wraps(view_func)
        @ratelimit(key=key, rate=rate, method=method, block=True)
        def wrapped_view(request, *args, **kwargs):
            # Check if request was rate limited
            if getattr(request, 'limited', False):
                return JsonResponse({
                    'error': 'Rate limit exceeded. Please try again later.',
                    'detail': f'Maximum {rate} requests allowed.'
                }, status=429)
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


# Predefined rate limits for different endpoint types

def strict_ratelimit(view_func):
    """Very strict rate limiting for sensitive operations (e.g., login, password reset)"""
    return api_ratelimit(key='user_or_ip', rate='5/m', method=['POST'])(view_func)


def moderate_ratelimit(view_func):
    """Moderate rate limiting for write operations"""
    return api_ratelimit(key='user', rate='60/m', method=['POST', 'PUT', 'PATCH', 'DELETE'])(view_func)


def relaxed_ratelimit(view_func):
    """Relaxed rate limiting for read operations"""
    return api_ratelimit(key='user', rate='200/m', method=['GET'])(view_func)


def public_ratelimit(view_func):
    """Rate limiting for public endpoints (no authentication required)"""
    return api_ratelimit(key='ip', rate='30/m')(view_func)
