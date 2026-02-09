#!/usr/bin/env python
"""Test script to simulate Vercel import behavior"""

import os
import sys

# Simulate Vercel environment
os.environ['VERCEL'] = '1'
os.environ['POSTGRES_URL'] = 'postgresql://test:test@localhost/test'

print("Simulating Vercel environment...")
print(f"  VERCEL={os.environ.get('VERCEL')}")
print(f"  POSTGRES_URL={os.environ.get('POSTGRES_URL')}")

# Try to import the app (this is what Vercel does)
print("\nAttempting to import app module...")
try:
    import app
    print("  [OK] App module imported")
except Exception as e:
    print(f"  [FAILED] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check if the WSGI handler is available
print("\nChecking WSGI handler...")
try:
    print(f"  app.app type: {type(app.app)}")
    print(f"  app.app is callable: {callable(app.app)}")
except Exception as e:
    print(f"  [FAILED] {e}")
    import traceback
    traceback.print_exc()

print("\nTest complete")
