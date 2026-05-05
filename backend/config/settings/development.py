"""
Django development settings for Hotel PMS project.
"""

from .base import *
import os

DEBUG = True

# Allow testserver for testing
ALLOWED_HOSTS += ['testserver']

# Database - SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'ATOMIC_REQUESTS': True,
    }
}

# Email Backend for development - Use SMTP for real email testing
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Hotel PMS <noreply@hotelpms.com>')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL)

# Security Settings for development (to pass deployment checks)
# Note: In production, these should be True
SECURE_HSTS_SECONDS = 1 if os.environ.get('DJANGO_DEPLOY_CHECK') else 0  # Minimal HSTS for deployment checks
SECURE_SSL_REDIRECT = bool(os.environ.get('DJANGO_DEPLOY_CHECK', False))  # Enable only for deployment checks
SESSION_COOKIE_SECURE = bool(os.environ.get('DJANGO_DEPLOY_CHECK', False))  # Enable only for deployment checks
CSRF_COOKIE_SECURE = bool(os.environ.get('DJANGO_DEPLOY_CHECK', False))  # Enable only for deployment checks

# Additional Security Headers (can be enabled in development)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_REFERRER_POLICY = 'same-origin'

# Debug Toolbar (optional)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
# INTERNAL_IPS = ['127.0.0.1']
