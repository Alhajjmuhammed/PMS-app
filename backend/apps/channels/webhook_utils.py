"""
Webhook signature validation utilities for secure OTA integration
"""

import hmac
import hashlib
import json
from typing import Dict, Any, Optional
from django.conf import settings


def generate_hmac_signature(payload: bytes, secret: str, algorithm: str = 'sha256') -> str:
    """
    Generate HMAC signature for webhook payload.
    
    Args:
        payload: Raw request body as bytes
        secret: Webhook secret key
        algorithm: Hash algorithm (sha256, sha1, sha512)
    
    Returns:
        Hex-encoded HMAC signature
    """
    if not secret:
        raise ValueError("Webhook secret cannot be empty")
    
    if algorithm == 'sha256':
        hash_func = hashlib.sha256
    elif algorithm == 'sha1':
        hash_func = hashlib.sha1
    elif algorithm == 'sha512':
        hash_func = hashlib.sha512
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hash_func
    ).hexdigest()
    
    return signature


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str,
    algorithm: str = 'sha256'
) -> bool:
    """
    Verify HMAC signature for webhook request.
    
    Args:
        payload: Raw request body as bytes
        signature: Signature from request header (hex-encoded)
        secret: Webhook secret key
        algorithm: Hash algorithm
    
    Returns:
        True if signature is valid, False otherwise
    """
    if not secret:
        return False
    
    if not signature:
        return False
    
    try:
        expected_signature = generate_hmac_signature(payload, secret, algorithm)
        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected_signature, signature.lower())
    except (ValueError, TypeError) as e:
        # Log specific errors for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Webhook signature verification failed: {str(e)}")
        return False


class WebhookValidator:
    """
    Channel-specific webhook validators.
    Different OTAs may use different signature algorithms and header formats.
    """
    
    @staticmethod
    def validate_booking_com(request, secret: str) -> bool:
        """
        Validate Booking.com webhook signature.
        Booking.com sends signature in X-Booking-Signature header using SHA256.
        """
        signature = request.headers.get('X-Booking-Signature', '')
        if not signature:
            return False
        
        return verify_webhook_signature(
            request.body,
            signature,
            secret,
            algorithm='sha256'
        )
    
    @staticmethod
    def validate_expedia(request, secret: str) -> bool:
        """
        Validate Expedia webhook signature.
        Expedia sends signature in X-Expedia-Signature header using SHA256.
        """
        signature = request.headers.get('X-Expedia-Signature', '')
        if not signature:
            return False
        
        return verify_webhook_signature(
            request.body,
            signature,
            secret,
            algorithm='sha256'
        )
    
    @staticmethod
    def validate_airbnb(request, secret: str) -> bool:
        """
        Validate Airbnb webhook signature.
        Airbnb sends signature in X-Airbnb-Signature header using SHA256.
        """
        signature = request.headers.get('X-Airbnb-Signature', '')
        if not signature:
            return False
        
        return verify_webhook_signature(
            request.body,
            signature,
            secret,
            algorithm='sha256'
        )
    
    @staticmethod
    def validate_generic(request, secret: str, header_name: str = 'X-Hub-Signature-256') -> bool:
        """
        Generic webhook signature validation.
        Looks for signature in specified header (default: X-Hub-Signature-256).
        Format: sha256=<signature>
        """
        signature_header = request.headers.get(header_name, '')
        if not signature_header:
            return False
        
        # Parse signature format like "sha256=abc123..."
        if '=' in signature_header:
            algorithm_part, signature = signature_header.split('=', 1)
            algorithm = algorithm_part.replace('sha', '')  # sha256 -> 256
            if algorithm == '256':
                algorithm = 'sha256'
            elif algorithm == '1':
                algorithm = 'sha1'
            elif algorithm == '512':
                algorithm = 'sha512'
        else:
            # No algorithm prefix, assume sha256
            signature = signature_header
            algorithm = 'sha256'
        
        return verify_webhook_signature(
            request.body,
            signature,
            secret,
            algorithm=algorithm
        )
    
    @classmethod
    def validate_by_channel(cls, request, channel_code: str, secret: str) -> bool:
        """
        Validate webhook signature based on channel type.
        
        Args:
            request: Django request object
            channel_code: Channel code (e.g., 'BOOKING', 'EXPEDIA')
            secret: Webhook secret
        
        Returns:
            True if signature is valid or no validation needed
        """
        if not secret:
            # If no secret configured, use generic validation with common headers
            for header in ['X-Hub-Signature-256', 'X-Signature', 'X-Webhook-Signature']:
                if request.headers.get(header):
                    return cls.validate_generic(request, secret or '', header)
            # No signature header found and no secret - reject
            return False
        
        channel_validators = {
            'BOOKING': cls.validate_booking_com,
            'EXPEDIA': cls.validate_expedia,
            'AIRBNB': cls.validate_airbnb,
        }
        
        validator = channel_validators.get(channel_code.upper())
        if validator:
            return validator(request, secret)
        
        # Default to generic validation
        return cls.validate_generic(request, secret)


def log_webhook_attempt(
    property_channel_id: int,
    request_data: Dict[str, Any],
    is_valid: bool,
    error: Optional[str] = None
):
    """
    Log webhook validation attempts for security auditing.
    
    Args:
        property_channel_id: PropertyChannel ID
        request_data: Webhook payload metadata (NOT full payload for privacy)
        is_valid: Whether signature was valid
        error: Error message if validation failed
    """
    import logging
    logger = logging.getLogger('channels.webhooks')
    
    log_data = {
        'property_channel_id': property_channel_id,
        'valid': is_valid,
        'timestamp': str(request_data.get('timestamp', '')),
        'source_ip': request_data.get('source_ip', 'unknown'),
    }
    
    if error:
        log_data['error'] = error
    
    if is_valid:
        logger.info(f"Valid webhook received: {log_data}")
    else:
        logger.warning(f"Invalid webhook attempt: {log_data}")
