#!/usr/bin/env python
"""
Script to fix Swagger schema generation issues by adding swagger_fake_view checks
"""

import os
import re

# Files and patterns to fix
fixes = [
    {
        'file': 'api/v1/rates/rate_plan_views.py',
        'patterns': [
            (
                r'def get_queryset\(self\):\s*return.*?property=self\.request\.user\.property',
                lambda m: m.group(0).replace(
                    'def get_queryset(self):',
                    'def get_queryset(self):\n        if getattr(self, \'swagger_fake_view\', False):\n            return {}.objects.none()\n       '.format(
                        m.group(0).split('return ')[1].split('.objects')[0]
                    )
                )
            )
        ]
    },
    {
        'file': 'api/v1/rates/views.py',
        'patterns': [
            (
                r'if self\.request\.user\.assigned_property:',
                'if hasattr(self.request.user, \'assigned_property\') and self.request.user.assigned_property:'
            )
        ]
    },
    {
        'file': 'api/v1/channels/channels_views.py',
        'patterns': [
            (
                r'property=self\.request\.user\.property',
                'property=getattr(self.request.user, \'property\', None)'
            )
        ]
    },
    {
        'file': 'api/v1/reports/reports_views.py',
        'patterns': [
            (
                r'property=self\.request\.user\.property',
                'property=getattr(self.request.user, \'property\', None)'
            )
        ]
    },
    {
        'file': 'api/v1/notifications/views.py',
        'patterns': [
            (
                r'if self\.request\.user\.assigned_property:',
                'if hasattr(self.request.user, \'assigned_property\') and self.request.user.assigned_property:'
            )
        ]
    }
]

def fix_file(filepath, patterns):
    """Apply regex fixes to a file."""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    for pattern, replacement in patterns:
        if callable(replacement):
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        else:
            content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed: {filepath}")
    else:
        print(f"No changes needed: {filepath}")

if __name__ == '__main__':
    for fix in fixes:
        fix_file(fix['file'], fix['patterns'])
    
    print("All Swagger fixes applied!")