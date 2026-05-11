"""
DEEP guest isolation test.
Covers every endpoint, every HTTP verb, edge cases, and data integrity.

Run from backend/:  python tests/test_guest_isolation_deep.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.development'

import django
django.setup()

from django.test import Client
from django.utils import timezone
import json

from apps.guests.models import Guest
from apps.accounts.models import User
from rest_framework.authtoken.models import Token

# ── helpers ──────────────────────────────────────────────────────────────────

c = Client()
PASS = 0
FAIL = 0

def tok(email):
    u = User.objects.get(email=email)
    Token.objects.filter(user=u).delete()
    t = Token.objects.create(user=u)
    t.created = timezone.now()
    t.save(update_fields=['created'])
    return {'HTTP_AUTHORIZATION': f'Token {t.key}'}

def check(label, condition, detail=''):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f'    [PASS] {label}')
    else:
        FAIL += 1
        print(f'    [FAIL] {label}  ← {detail}')

def section(title):
    print()
    print('  ' + '─' * 60)
    print(f'  {title}')
    print('  ' + '─' * 60)

# ── tokens ───────────────────────────────────────────────────────────────────
FD   = tok('frontdesk@hotel.com')      # P1 — Grand Hotel Demo
FD2  = tok('frontdesk2@hotel.com')     # P1 — Grand Hotel Demo
MGR  = tok('manager@hotel.com')        # P1 — Grand Hotel Demo
ADM  = tok('admin@hotel.com')          # P2 — Lukman
MN   = tok('mn@gmail.com')             # P2 — Lukman
LMG  = tok('alhajjmuhammed@gmail.com') # P2 — Lukman

print('=' * 65)
print('  DEEP GUEST ISOLATION TEST')
print('  P1 = Grand Hotel Demo   P2 = Lukman')
print('=' * 65)

# ── Seed 5 guests per property ───────────────────────────────────────────────
section('SETUP — creating 5 real guests per property')

P1_RAW = [
    {'first_name':'James',   'last_name':'Hartley', 'email':'j.hartley@test.com',  'phone':'0712001001','nationality':'British',  'gender':'M','id_type':'passport',   'id_number':'GB10001001','city':'London',     'country':'United Kingdom'},
    {'first_name':'Amina',   'last_name':'Osei',    'email':'a.osei@test.com',      'phone':'0712001002','nationality':'Ghanaian', 'gender':'F','id_type':'national_id','id_number':'GH10001002','city':'Accra',      'country':'Ghana'},
    {'first_name':'Carlos',  'last_name':'Mendes',  'email':'c.mendes@test.com',    'phone':'0712001003','nationality':'Brazilian','gender':'M','id_type':'passport',   'id_number':'BR10001003','city':'Sao Paulo',  'country':'Brazil'},
    {'first_name':'Yuki',    'last_name':'Tanaka',  'email':'y.tanaka@test.com',    'phone':'0712001004','nationality':'Japanese', 'gender':'F','id_type':'passport',   'id_number':'JP10001004','city':'Tokyo',      'country':'Japan'},
    {'first_name':'Erik',    'last_name':'Hansen',  'email':'e.hansen@test.com',    'phone':'0712001005','nationality':'Danish',   'gender':'M','id_type':'passport',   'id_number':'DK10001005','city':'Copenhagen', 'country':'Denmark'},
]
P2_RAW = [
    {'first_name':'Fatima',  'last_name':'Rashidi', 'email':'f.rashidi@test.com',   'phone':'0723002001','nationality':'Emirati',  'gender':'F','id_type':'passport',   'id_number':'AE20002001','city':'Dubai',      'country':'UAE'},
    {'first_name':'Mohammed','last_name':'Yusuf',   'email':'m.yusuf@test.com',     'phone':'0723002002','nationality':'Nigerian', 'gender':'M','id_type':'national_id','id_number':'NG20002002','city':'Lagos',      'country':'Nigeria'},
    {'first_name':'Sofia',   'last_name':'Ramirez', 'email':'s.ramirez@test.com',   'phone':'0723002003','nationality':'Mexican',  'gender':'F','id_type':'passport',   'id_number':'MX20002003','city':'Mexico City','country':'Mexico'},
    {'first_name':'Liam',    'last_name':'Murphy',  'email':'l.murphy@test.com',    'phone':'0723002004','nationality':'Irish',    'gender':'M','id_type':'passport',   'id_number':'IE20002004','city':'Dublin',     'country':'Ireland'},
    {'first_name':'Priya',   'last_name':'Sharma',  'email':'p.sharma@test.com',    'phone':'0723002005','nationality':'Indian',   'gender':'F','id_type':'passport',   'id_number':'IN20002005','city':'Mumbai',     'country':'India'},
]

p1_ids, p2_ids = [], []
for g in P1_RAW:
    r = c.post('/api/v1/guests/', data=json.dumps(g), content_type='application/json', **FD)
    assert r.status_code == 201, f'P1 seed: {r.json()}'
    p1_ids.append(r.json()['id'])
    print(f'    P1 id={r.json()["id"]:>3}  {g["first_name"]:>8} {g["last_name"]:<9}  [{g["nationality"]}]  {g["id_number"]}')

for g in P2_RAW:
    r = c.post('/api/v1/guests/', data=json.dumps(g), content_type='application/json', **ADM)
    assert r.status_code == 201, f'P2 seed: {r.json()}'
    p2_ids.append(r.json()['id'])
    print(f'    P2 id={r.json()["id"]:>3}  {g["first_name"]:>8} {g["last_name"]:<9}  [{g["nationality"]}]  {g["id_number"]}')

# ══════════════════════════════════════════════════════════════════════════════
# 1. LIST ENDPOINT — GET /api/v1/guests/
# ══════════════════════════════════════════════════════════════════════════════
section('1. LIST ENDPOINT  GET /api/v1/guests/')

for label, hdr, own, other in [
    ('FD  (P1)', FD,  p1_ids, p2_ids),
    ('FD2 (P1)', FD2, p1_ids, p2_ids),
    ('MGR (P1)', MGR, p1_ids, p2_ids),
    ('ADM (P2)', ADM, p2_ids, p1_ids),
    ('MN  (P2)', MN,  p2_ids, p1_ids),
    ('LMG (P2)', LMG, p2_ids, p1_ids),
]:
    r = c.get('/api/v1/guests/', **hdr)
    ids = [g['id'] for g in r.json().get('results', r.json())]
    check(f'{label}  sees all 5 own guests',      all(i in ids for i in own),         f'missing: {[i for i in own if i not in ids]}')
    check(f'{label}  sees zero other-prop guests', not any(i in ids for i in other),   f'leaked: {[i for i in other if i in ids]}')

# ══════════════════════════════════════════════════════════════════════════════
# 2. SEARCH ENDPOINT — GET /api/v1/guests/search/?q=
# ══════════════════════════════════════════════════════════════════════════════
section('2. SEARCH ENDPOINT  GET /api/v1/guests/search/?q=')

# Search for a name that exists in both properties
for label, hdr, should_find, should_miss in [
    ('FD  (P1) search "James"',   FD,  'James',   'Fatima'),
    ('ADM (P2) search "Fatima"',  ADM, 'Fatima',  'James'),
    ('FD  (P1) search "Sha"',     FD,  None,      'Sharma'),   # "Priya Sharma" is P2 only
    ('ADM (P2) search "Han"',     ADM, None,      'Hansen'),   # "Erik Hansen" is P1 only
]:
    q = should_find or (should_miss or 'xx')
    r = c.get(f'/api/v1/guests/search/?q={q}', **hdr)
    results = r.json().get('results', [])
    names = [f'{g["first_name"]} {g["last_name"]}' for g in results]

    if should_find:
        check(f'{label} → finds "{should_find}"', any(should_find in n for n in names), f'got: {names}')
    if should_miss:
        check(f'{label} → does NOT see "{should_miss}"', not any(should_miss in n for n in names), f'leaked: {names}')

# Cross-property search: FD searches by P2 guest's passport number
p2_passport = P2_RAW[0]['id_number']  # AE20002001 (Fatima, P2)
r = c.get(f'/api/v1/guests/search/?q={p2_passport}', **FD)
results = r.json().get('results', [])
check('FD (P1) search by P2 passport → 0 results', len(results) == 0, f'got {len(results)} results: {results}')

# Cross-property search: ADM searches by P1 guest's phone
p1_phone = P1_RAW[1]['phone']  # Amina's phone
r = c.get(f'/api/v1/guests/search/?q={p1_phone}', **ADM)
results = r.json().get('results', [])
check('ADM (P2) search by P1 phone → 0 results', len(results) == 0, f'got {len(results)} results: {results}')

# ══════════════════════════════════════════════════════════════════════════════
# 3. FILTERING & ORDERING  GET /api/v1/guests/?nationality=British
# ══════════════════════════════════════════════════════════════════════════════
section('3. FILTERING & ORDERING (nationality, is_blacklisted, ordering)')

r = c.get('/api/v1/guests/?nationality=British', **FD)
ids = [g['id'] for g in r.json().get('results', r.json())]
check('FD filter nationality=British → only P1 British guest', all(i in p1_ids for i in ids), f'foreign ids: {[i for i in ids if i not in p1_ids]}')

r = c.get('/api/v1/guests/?nationality=Nigerian', **FD)
ids = [g['id'] for g in r.json().get('results', r.json())]
check('FD filter nationality=Nigerian → 0 results (P2 guest)', len(ids) == 0, f'got {ids}')

r = c.get('/api/v1/guests/?ordering=last_name', **ADM)
ids = [g['id'] for g in r.json().get('results', r.json())]
check('ADM ordered list → only P2 ids', all(i in p2_ids for i in ids), f'foreign: {[i for i in ids if i not in p2_ids]}')

# ══════════════════════════════════════════════════════════════════════════════
# 4. DETAIL ENDPOINT — GET /PATCH /DELETE /api/v1/guests/<id>/
# ══════════════════════════════════════════════════════════════════════════════
section('4. DETAIL  GET · PATCH · DELETE cross-property → 404')

for p1id in p1_ids:
    r = c.get(f'/api/v1/guests/{p1id}/', **ADM)
    check(f'ADM GET  P1 guest {p1id} → 404', r.status_code == 404, f'got {r.status_code}')

for p2id in p2_ids:
    r = c.get(f'/api/v1/guests/{p2id}/', **FD)
    check(f'FD  GET  P2 guest {p2id} → 404', r.status_code == 404, f'got {r.status_code}')

for p2id in p2_ids:
    r = c.patch(f'/api/v1/guests/{p2id}/', data=json.dumps({'city': 'HACKED'}), content_type='application/json', **FD)
    check(f'FD  PATCH P2 guest {p2id} → 404', r.status_code == 404, f'got {r.status_code}')

for p1id in p1_ids:
    r = c.patch(f'/api/v1/guests/{p1id}/', data=json.dumps({'city': 'HACKED'}), content_type='application/json', **ADM)
    check(f'ADM PATCH P1 guest {p1id} → 404', r.status_code == 404, f'got {r.status_code}')

for p2id in p2_ids:
    r = c.delete(f'/api/v1/guests/{p2id}/', **MGR)
    check(f'MGR DEL  P2 guest {p2id} → 404', r.status_code == 404, f'got {r.status_code}')

# ══════════════════════════════════════════════════════════════════════════════
# 5. OWN-PROPERTY CRUD STILL WORKS
# ══════════════════════════════════════════════════════════════════════════════
section('5. OWN-PROPERTY CRUD (must still work after isolation)')

# FD reads own guest
r = c.get(f'/api/v1/guests/{p1_ids[0]}/', **FD)
check('FD  GET  own guest → 200', r.status_code == 200, f'{r.status_code}')
check('FD  GET  own guest → correct name', r.json()['first_name'] == 'James', f'{r.json().get("first_name")}')

# MGR edits own guest city
r = c.patch(f'/api/v1/guests/{p1_ids[2]}/', data=json.dumps({'city': 'Rio de Janeiro'}), content_type='application/json', **MGR)
check('MGR PATCH own guest → 200', r.status_code == 200, f'{r.status_code}')
check('MGR PATCH own guest → city updated', r.json().get('city') == 'Rio de Janeiro', f'{r.json().get("city")}')

# ADM edits own guest
r = c.patch(f'/api/v1/guests/{p2_ids[1]}/', data=json.dumps({'city': 'Abuja'}), content_type='application/json', **ADM)
check('ADM PATCH own guest → 200', r.status_code == 200, f'{r.status_code}')
check('ADM PATCH own guest → city updated', r.json().get('city') == 'Abuja', f'{r.json().get("city")}')

# FD2 (same property as FD) can also see FD's guests
r = c.get('/api/v1/guests/', **FD2)
ids = [g['id'] for g in r.json().get('results', r.json())]
check('FD2 (same P1) sees all P1 guests incl those created by FD', all(i in ids for i in p1_ids), f'missing: {[i for i in p1_ids if i not in ids]}')

# LMG (P2 manager) creates a guest — should auto-tag to P2
r = c.post('/api/v1/guests/', data=json.dumps({'first_name':'Test','last_name':'LMGCreate','phone':'0799999001'}), content_type='application/json', **LMG)
check('LMG create guest → 201', r.status_code == 201, f'{r.json()}')
if r.status_code == 201:
    new_id = r.json()['id']
    db = Guest.objects.get(id=new_id)
    check('LMG created guest → auto-tagged P2', str(db.home_property) == 'Lukman (LKY)', f'got "{db.home_property}"')
    check('FD (P1) cannot see LMG-created guest', new_id not in [g['id'] for g in c.get('/api/v1/guests/', **FD).json().get('results', [])], 'leaked')
    Guest.objects.filter(id=new_id).delete()

# ══════════════════════════════════════════════════════════════════════════════
# 6. /guests/create/ ENDPOINT (legacy)
# ══════════════════════════════════════════════════════════════════════════════
section('6. LEGACY CREATE  POST /api/v1/guests/create/')

r = c.post('/api/v1/guests/create/', data=json.dumps({'first_name':'Legacy','last_name':'Create','phone':'0799999002'}), content_type='application/json', **FD)
check('FD POST /guests/create/ → 201', r.status_code == 201, f'{r.json()}')
if r.status_code == 201:
    new_id = r.json()['id']
    db = Guest.objects.get(id=new_id)
    check('Legacy create → auto-tagged P1', 'Grand Hotel Demo' in str(db.home_property), f'got "{db.home_property}"')
    check('ADM (P2) cannot see legacy-created P1 guest', new_id not in [g['id'] for g in c.get('/api/v1/guests/', **ADM).json().get('results', [])], 'leaked')
    Guest.objects.filter(id=new_id).delete()

# ══════════════════════════════════════════════════════════════════════════════
# 7. NULL home_property GUEST (pre-existing guest with no property)
# ══════════════════════════════════════════════════════════════════════════════
section('7. EDGE CASE — guest with NULL home_property')

# This simulates a guest that existed before the migration
orphan = Guest.objects.create(first_name='Orphan', last_name='NoProperty', phone='0799000999')
check('Orphan guest has null home_property', orphan.home_property is None, str(orphan.home_property))

# Neither property should see it
r = c.get('/api/v1/guests/', **FD)
fd_ids = [g['id'] for g in r.json().get('results', r.json())]
check('FD (P1) does NOT see null-property guest', orphan.id not in fd_ids, f'leaked id={orphan.id}')

r = c.get('/api/v1/guests/', **ADM)
adm_ids = [g['id'] for g in r.json().get('results', r.json())]
check('ADM (P2) does NOT see null-property guest', orphan.id not in adm_ids, f'leaked id={orphan.id}')

# Direct GET/PATCH/DELETE by either side should 404
r = c.get(f'/api/v1/guests/{orphan.id}/', **FD)
check('FD  GET  null-property guest → 404', r.status_code == 404, f'got {r.status_code}')
r = c.patch(f'/api/v1/guests/{orphan.id}/', data=json.dumps({'city': 'HACKED'}), content_type='application/json', **ADM)
check('ADM PATCH null-property guest → 404', r.status_code == 404, f'got {r.status_code}')
orphan.delete()

# ══════════════════════════════════════════════════════════════════════════════
# 8. DATA INTEGRITY — no record was silently mutated
# ══════════════════════════════════════════════════════════════════════════════
section('8. DATA INTEGRITY — no cross-property PATCH silently succeeded')

mutated = []
for gid in p1_ids + p2_ids:
    try:
        db = Guest.objects.get(id=gid)
        if db.city == 'HACKED':
            mutated.append(gid)
    except Guest.DoesNotExist:
        pass

check('No guest record was mutated by cross-property PATCH', len(mutated) == 0, f'mutated ids: {mutated}')

# ══════════════════════════════════════════════════════════════════════════════
# 9. PAGINATION — second page must also be isolated
# ══════════════════════════════════════════════════════════════════════════════
section('9. PAGINATION — page_size=2, page 2 must still be isolated')

r = c.get('/api/v1/guests/?page_size=2&page=2', **FD)
if r.status_code == 200:
    page2_ids = [g['id'] for g in r.json().get('results', r.json())]
    leaked = [i for i in page2_ids if i in p2_ids]
    check('FD page 2 contains no P2 guests', len(leaked) == 0, f'leaked: {leaked}')
else:
    check('FD page 2 request → no server error', r.status_code in [200, 404], f'{r.status_code}')

# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print()
print('=' * 65)
print(f'  TOTAL CHECKS : {PASS + FAIL}')
print(f'  PASSED       : {PASS}')
print(f'  FAILED       : {FAIL}')
print('=' * 65)
if FAIL == 0:
    print('  RESULT: ALL CHECKS PASSED — isolation is airtight.')
else:
    print('  RESULT: SOME CHECKS FAILED — see [FAIL] lines above.')
print('=' * 65)

# Cleanup
Guest.objects.filter(id__in=p1_ids + p2_ids).delete()
print('  Cleanup done.')
