"""
Caching utilities for expensive queries and operations.
"""

from django.core.cache import cache
from functools import wraps
from django.db.models import QuerySet
import hashlib
import json


def cache_queryset(timeout=300, key_prefix='qs'):
    """
    Decorator to cache queryset results.
    
    Usage:
        @cache_queryset(timeout=600, key_prefix='rooms')
        def get_available_rooms(property_id, date):
            return Room.objects.filter(...)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key_parts = [key_prefix, func.__name__]
            
            # Add args to key
            for arg in args:
                if isinstance(arg, (int, str, bool)):
                    cache_key_parts.append(str(arg))
            
            # Add kwargs to key
            for k, v in sorted(kwargs.items()):
                if isinstance(v, (int, str, bool)):
                    cache_key_parts.append(f"{k}_{v}")
            
            cache_key = '_'.join(cache_key_parts)
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache the result
            if isinstance(result, QuerySet):
                # Evaluate queryset before caching
                result = list(result)
            
            cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern):
    """
    Invalidate all cache keys matching a pattern.
    
    Usage:
        invalidate_cache_pattern('rooms_*')
    """
    try:
        cache.delete_pattern(pattern)
    except AttributeError:
        # Not using Redis, can't delete by pattern
        pass


class CacheManager:
    """Cache manager for common operations."""
    
    @staticmethod
    def get_room_availability(property_id, date_str, timeout=600):
        """Cache room availability for a specific date."""
        cache_key = f'availability_{property_id}_{date_str}'
        return cache.get(cache_key)
    
    @staticmethod
    def set_room_availability(property_id, date_str, data, timeout=600):
        """Set room availability cache."""
        cache_key = f'availability_{property_id}_{date_str}'
        cache.set(cache_key, data, timeout)
    
    @staticmethod
    def invalidate_room_availability(property_id):
        """Invalidate all room availability cache for a property."""
        invalidate_cache_pattern(f'availability_{property_id}_*')
    
    @staticmethod
    def get_dashboard_stats(property_id, date_str, timeout=300):
        """Cache dashboard statistics."""
        cache_key = f'dashboard_{property_id}_{date_str}'
        return cache.get(cache_key)
    
    @staticmethod
    def set_dashboard_stats(property_id, date_str, data, timeout=300):
        """Set dashboard statistics cache."""
        cache_key = f'dashboard_{property_id}_{date_str}'
        cache.set(cache_key, data, timeout)
    
    @staticmethod
    def get_report_data(report_type, property_id, params_hash, timeout=1800):
        """Cache report data (30 min default)."""
        cache_key = f'report_{report_type}_{property_id}_{params_hash}'
        return cache.get(cache_key)
    
    @staticmethod
    def set_report_data(report_type, property_id, params_hash, data, timeout=1800):
        """Set report data cache."""
        cache_key = f'report_{report_type}_{property_id}_{params_hash}'
        cache.set(cache_key, data, timeout)
    
    @staticmethod
    def get_rate_plan(rate_plan_id, date_str, timeout=3600):
        """Cache rate plan pricing (1 hour)."""
        cache_key = f'rate_plan_{rate_plan_id}_{date_str}'
        return cache.get(cache_key)
    
    @staticmethod
    def set_rate_plan(rate_plan_id, date_str, data, timeout=3600):
        """Set rate plan cache."""
        cache_key = f'rate_plan_{rate_plan_id}_{date_str}'
        cache.set(cache_key, data, timeout)
    
    @staticmethod
    def invalidate_rate_plans(property_id):
        """Invalidate all rate plan caches for a property."""
        invalidate_cache_pattern(f'rate_plan_*')
