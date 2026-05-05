# Hotel PMS Configuration Package
# Make Celery app available when running Celery workers/beat.
# Guard: skip Celery import during Django web server, management commands,
# and test runs to avoid hanging when the broker (Redis) is unavailable.
import sys as _sys

_argv0 = (_sys.argv[0] if _sys.argv else '').lower()
_running_celery = 'celery' in _argv0

if _running_celery:
    from .celery import app as celery_app  # noqa
    __all__ = ('celery_app',)
