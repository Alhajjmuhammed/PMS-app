#!/usr/bin/env python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

import importlib
from pathlib import Path

errors = []
skipped = []

for p in sorted(Path('.').rglob('*.py')):
    s = str(p)
    if any(x in s for x in ['__pycache__', 'venv/', 'migrations/', 'test_', '/tests/', 'debug_', 'diag', 'check_imports']):
        continue
    mod = s.removesuffix('.py').replace('/', '.')
    if mod.startswith('.') or mod in ('manage',):
        continue
    try:
        importlib.import_module(mod)
    except Exception as e:
        errors.append((mod, type(e).__name__, str(e)))

if errors:
    for m, t, e in errors:
        print(f'ERROR [{t}] in {m}: {e}')
else:
    print('All modules imported OK — no errors found')
