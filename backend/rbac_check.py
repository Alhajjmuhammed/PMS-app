import urllib.request, logging
logging.disable(logging.CRITICAL)

BASE = 'http://localhost:8000/api/v1'
TOKENS = {
    'SUPERADMIN': '1baf9c913991c8aa5bba8e8be5749bc798dae13a',
    'MANAGER': 'dc7029d05befa8f361e74a9c56be0b04ec4ffaaa',
    'FRONT_DESK': 'fcdce3711f015cdab7b635971ca97772f82984f8',
    'HOUSEKEEPING': '4653bc2a70a78a107f2ee4b919091ed503fa2c26',
    'MAINTENANCE': '8bba687a713664736f19e1acf9fbafbceebc39dd',
    'ACCOUNTANT': '7e59d04ab0300df6aef781bde43d2b573dddc999',
    'POS_STAFF': '810ff308ee0c9193934e915ce893f72123a5f820',
    'GUEST': '68e224072cbd1ef297b43e0c7978307b9d7c7383',
}
MATRIX = {
    '/properties/': ['SUPERADMIN', 'MANAGER'],
    '/rooms/': ['SUPERADMIN', 'MANAGER', 'FRONT_DESK'],
    '/frontdesk/check-ins/': ['SUPERADMIN', 'MANAGER', 'FRONT_DESK'],
    '/frontdesk/check-outs/': ['SUPERADMIN', 'MANAGER', 'FRONT_DESK'],
    '/housekeeping/tasks/': ['SUPERADMIN', 'MANAGER', 'HOUSEKEEPING'],
    '/pos/menu-items/': ['SUPERADMIN', 'MANAGER', 'POS_STAFF'],
    '/billing/folios/': ['SUPERADMIN', 'MANAGER', 'ACCOUNTANT'],
    '/maintenance/requests/': ['SUPERADMIN', 'MANAGER', 'MAINTENANCE'],
    '/guests/preferences/': ['SUPERADMIN', 'MANAGER', 'FRONT_DESK'],
    '/guests/documents/': ['SUPERADMIN', 'MANAGER', 'FRONT_DESK'],
    '/reports/daily-stats/': ['SUPERADMIN', 'MANAGER'],
    '/reports/templates/': ['SUPERADMIN', 'MANAGER', 'ACCOUNTANT'],
    '/billing/cashier-shifts/': ['SUPERADMIN', 'MANAGER', 'ACCOUNTANT', 'POS_STAFF'],
    '/rates/rate-plans/': ['SUPERADMIN', 'MANAGER'],
    '/rates/plans/active/': ['SUPERADMIN', 'MANAGER', 'FRONT_DESK'],
    '/rooms/types/': ['SUPERADMIN', 'MANAGER', 'FRONT_DESK'],
}

issues = 0
total = 0
for ep, allowed in MATRIX.items():
    for role, tok in TOKENS.items():
        try:
            req = urllib.request.Request(BASE + ep, headers={'Authorization': 'Token ' + tok})
            code = urllib.request.urlopen(req, timeout=3).getcode()
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception:
            code = 0
        should = role in allowed
        ok = (code in [200, 201, 400]) if should else (code == 403)
        total += 1
        if not ok:
            print(f'ISSUE: {ep} role={role} expected={"ALLOW" if should else "DENY"} got={code}')
            issues += 1

print(f'\nRESULT: {total} checks, ISSUES={issues}')
if issues == 0:
    print('100% CLEAN')
