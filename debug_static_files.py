#!/usr/bin/env python
"""
Debug script for static files issues on Render
Run this on your Render instance via Shell to diagnose issues
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from pathlib import Path
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage

print("=== STATIC FILES DEBUGGING ===\n")

# Basic settings
print("1. Basic Configuration:")
print(f"   DEBUG: {settings.DEBUG}")
print(f"   STATIC_URL: {settings.STATIC_URL}")
print(f"   STATIC_ROOT: {settings.STATIC_ROOT}")
print(f"   STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
print()

# Environment
print("2. Environment:")
print(f"   Is Render: {'RENDER' in os.environ}")
print(f"   Python version: {sys.version}")
print(f"   Django version: {django.VERSION}")
print()

# WhiteNoise check
print("3. WhiteNoise Configuration:")
try:
    import whitenoise
    print(f"   WhiteNoise version: {whitenoise.__version__}")
except ImportError:
    print("   WhiteNoise: NOT INSTALLED!")

print(f"   WhiteNoise in middleware: {'whitenoise.middleware.WhiteNoiseMiddleware' in settings.MIDDLEWARE}")
print(f"   Storage backend: {staticfiles_storage.__class__.__name__}")
print()

# Static files existence
print("4. Static Files Check:")
static_root = Path(settings.STATIC_ROOT)
print(f"   Static root exists: {static_root.exists()}")
print(f"   Static root is directory: {static_root.is_dir()}")

if static_root.exists() and static_root.is_dir():
    css_files = list(static_root.rglob('*.css'))
    print(f"   Total CSS files: {len(css_files)}")
    if css_files:
        print("   Sample CSS files:")
        for f in css_files[:5]:
            print(f"      - {f.relative_to(static_root)}")
else:
    print("   WARNING: Static root doesn't exist or isn't a directory!")
print()

# Test specific file
print("5. Testing auth.css:")
auth_css = static_root / 'css' / 'auth.css'
print(f"   File exists: {auth_css.exists()}")
print(f"   File path: {auth_css}")

# Test URL generation
from django.templatetags.static import static
try:
    url = static('css/auth.css')
    print(f"   Generated URL: {url}")
except Exception as e:
    print(f"   ERROR generating URL: {e}")

# Test finder
found = finders.find('css/auth.css')
print(f"   Found by finder: {found is not None}")
if found:
    print(f"   Finder path: {found}")
print()

# Storage test
print("6. Storage Test:")
try:
    exists = staticfiles_storage.exists('css/auth.css')
    print(f"   Storage says file exists: {exists}")
    if exists:
        url = staticfiles_storage.url('css/auth.css')
        print(f"   Storage URL: {url}")
except Exception as e:
    print(f"   Storage error: {e}")

print("\n=== END DEBUG ===")
