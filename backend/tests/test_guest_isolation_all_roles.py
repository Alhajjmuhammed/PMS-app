"""
Comprehensive per-property guest isolation test.
Covers all 11 users across every role at both properties.
Run from backend/: python tests/test_guest_isolation_all_roles.py
"""
import os
import sys

# Ensure the backend root is on sys.path so 'config' and 'apps' are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.development'

import django
django.setup()

from django.test import Client
import json
from django.utils import timezone
from apps.guests.models import Guest
from apps.accounts.models import User
from rest_framework.authtoken.models import Token

c = Client()

ALL_USERS = [
    ('FRONT_DESK',   'frontdesk@hotel.com',      'P1'),
    ('FRONT_DESK-2', 'frontdesk2@hotel.com',      'P1'),
    ('MANAGER',      'manager@hotel.com',          'P1'),
    ('ACCOUNTANT',   'accountant@hotel.com',       'P1'),
    ('HOUSEKEEPING', 'housekeeping@hotel.com',     'P1'),
    ('MAINTENANCE',  'maintenance@hotel.com',      'P1'),
    ('POS_STAFF',    'pos@hotel.com',              'P1'),
    ('GUEST_ROLE',   'guest@hotel.com',            'P1'),
    ('ADMIN-LKY',    'admin@hotel.com',            'P2'),
    ('ADMIN-MN',     'mn@gmail.com',               'P2'),
    ('MANAGER-LKY',  'alhajjmuhammed@gmail.com',   'P2'),
]

# ── STEP 1: Generate Knox tokens directly (bypasses login rate limiter) ─────
print('=' * 65)
print('STEP 1: TOKEN GENERATION (direct Knox, no rate-limit hit)')
print('=' * 65)
tokens = {}
for (label, email, prop_tag) in ALL_USERS:
    u = User.objects.get(email=email)
    # Delete any old/expired token and create a fresh one
    Token.objects.filter(user=u).delete()
    tok = Token.objects.create(user=u)
    # Stamp created = now so it's not expired
    tok.created = timezone.now()
    tok.save(update_fields=['created'])
    tokens[label] = {'tok': tok.key, 'prop': prop_tag, 'email': email, 'role': u.role}
    print(f'  [OK ] {label:<15} role={u.role:<15} prop={prop_tag}  {email}')


def H(label):
    return {'HTTP_AUTHORIZATION': f'Token {tokens[label]["tok"]}'}


# ── STEP 2: Create one seed guest per property ───────────────────────────────
print()
print('=' * 65)
print('STEP 2: CREATE SEED GUESTS')
print('=' * 65)

r = c.post(
    '/api/v1/guests/',
    data=json.dumps({'first_name': 'Seed', 'last_name': 'GrandHotel', 'phone': '0799100001'}),
    content_type='application/json', **H('FRONT_DESK'))
assert r.status_code == 201, f'P1 seed failed: {r.json()}'
gid_p1 = r.json()['id']
g = Guest.objects.get(id=gid_p1)
print(f'  P1 seed guest id={gid_p1}, home="{g.home_property}"')

r = c.post(
    '/api/v1/guests/',
    data=json.dumps({'first_name': 'Seed', 'last_name': 'Lukman', 'phone': '0799200002'}),
    content_type='application/json', **H('ADMIN-LKY'))
assert r.status_code == 201, f'P2 seed failed: {r.json()}'
gid_p2 = r.json()['id']
g = Guest.objects.get(id=gid_p2)
print(f'  P2 seed guest id={gid_p2}, home="{g.home_property}"')

# ── STEP 3: Isolation matrix ─────────────────────────────────────────────────
print()
print('=' * 65)
print('STEP 3: ISOLATION MATRIX')
print('=' * 65)
print(f'  {"USER":<15} {"ROLE":<15} {"P":<3} {"own in list":<12} {"other in list":<15} {"GET other":<11} {"DEL other":<11}')
print('  ' + '-' * 75)

all_pass = True
rows = []

for (label, email, prop_tag) in ALL_USERS:
    own   = gid_p1 if prop_tag == 'P1' else gid_p2
    other = gid_p2 if prop_tag == 'P1' else gid_p1
    role  = tokens[label]['role']
    Hdr   = H(label)

    # --- List ---
    r_list = c.get('/api/v1/guests/', **Hdr)
    if r_list.status_code == 200:
        ids = [g['id'] for g in r_list.json().get('results', r_list.json())]
        list_own   = own in ids
        list_other = other in ids
    else:
        list_own   = None  # role has no list access (403)
        list_other = None

    # --- GET detail of OTHER property's guest ---
    r_det = c.get(f'/api/v1/guests/{other}/', **Hdr)

    # --- DELETE OTHER property's guest ---
    r_del = c.delete(f'/api/v1/guests/{other}/', **Hdr)

    col_own   = '✓ yes'   if list_own  else ('N/A' if list_own  is None else '✗ missing')
    col_other = '✓ hidden' if (list_other is False) else ('N/A' if list_other is None else '✗ LEAK')
    col_det   = f'✓ {r_det.status_code}' if r_det.status_code in [403, 404] else f'✗ {r_det.status_code}'
    col_del   = f'✓ {r_del.status_code}' if r_del.status_code in [403, 404, 405] else f'✗ {r_del.status_code}'

    row_pass = (
        (list_other is False or list_other is None)
        and r_det.status_code in [403, 404]
        and r_del.status_code in [403, 404, 405]
    )
    if not row_pass:
        all_pass = False

    flag = '' if row_pass else '  ← FAIL'
    print(f'  {label:<15} {role:<15} {prop_tag:<3} {col_own:<12} {col_other:<15} {col_det:<11} {col_del:<11}{flag}')
    rows.append((label, row_pass))

print()
print('=' * 65)
if all_pass:
    print('RESULT: ALL 11 USERS PASS  ✓')
    print('Complete per-property guest isolation confirmed.')
else:
    failed = [l for l, ok in rows if not ok]
    print(f'RESULT: FAILED for: {failed}')
print('=' * 65)

# ── Cleanup ──────────────────────────────────────────────────────────────────
Guest.objects.filter(id__in=[gid_p1, gid_p2]).delete()
print('Seed guests cleaned up.')
