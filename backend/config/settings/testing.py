"""
Django test settings — fast, no file I/O, no external services.
Inherits from development, then overrides anything that would hang
(file-based logging handlers, Redis cache when Redis isn't running, etc.)
"""

from .development import *

# ── Logging: console-only, no RotatingFileHandler ─────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
        'django.request': {'handlers': ['console'], 'level': 'ERROR', 'propagate': False},
    },
}

# ── Cache: local memory only — no Redis connection required ───────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'hotel-pms-test-cache',
    }
}

# Keep silencing ratelimit checks (same as base.py LocMemCache branch)
SILENCED_SYSTEM_CHECKS = ['django_ratelimit.E003', 'django_ratelimit.W001']

# ── Celery: run tasks synchronously in tests ─────────────────────────────
# Also remove django_celery_beat from INSTALLED_APPS — it imports celery at
# startup and celery hangs on this environment when Redis is not running.
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django_celery_beat']
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ── Email: discard silently ──────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# ── Password hashing: fast hasher for tests ─────────────────────────────
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# ── Database: use in-memory SQLite for fully isolated tests ──────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
