import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.testing'
django.setup()
from django.urls import resolve, Resolver404
tests = [
    '/api/v1/billing/cashier-shifts/current/',
    '/api/v1/rooms/types/active/',
    '/api/v1/rooms/blocks/active/',
    '/api/v1/rooms/blocks/by-date/',
    '/api/v1/rooms/blocks/stats/',
    '/api/v1/rooms/amenities/active/',
    '/api/v1/rooms/status-logs/room/1/',
]
for u in tests:
    try:
        r = resolve(u)
        print(u, '->', r.url_name, r.func.cls.__name__)
    except Resolver404 as e:
        print(u, 'Resolver404:', str(e)[:80])
    except Exception as e:
        print(u, 'ERR:', type(e).__name__, str(e)[:80])
