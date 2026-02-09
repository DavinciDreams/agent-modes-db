#!/usr/bin/env python
"""Test script to diagnose Flask app loading issues"""

import sys
import traceback

print("=" * 60)
print("FLASK APP LOADING DIAGNOSTICS")
print("=" * 60)

# Test 1: Import database module
print("\n[1] Testing database module import...")
try:
    import database as db
    print("    [OK] Database module imported successfully")
    print(f"    - USE_POSTGRES: {db.USE_POSTGRES}")
    print(f"    - POSTGRES_AVAILABLE: {db.POSTGRES_AVAILABLE}")
    print(f"    - DB_FILE: {db.DB_FILE}")
except Exception as e:
    print(f"    [FAILED] {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Test connection pooling function
print("\n[2] Testing connection pooling function...")
try:
    pool_func = db.get_postgres_pool
    print("    [OK] get_postgres_pool function exists")
except Exception as e:
    print(f"    [FAILED] {e}")
    traceback.print_exc()

# Test 3: Test database context manager
print("\n[3] Testing database context manager...")
try:
    with db.get_db() as conn:
        print("    [OK] Database context manager works")
        print(f"    - Connection type: {type(conn)}")
except Exception as e:
    print(f"    [FAILED] {e}")
    traceback.print_exc()

# Test 4: Import Flask app
print("\n[4] Testing Flask app import...")
try:
    from app import app
    print("    [OK] Flask app imported successfully")
    print(f"    - App type: {type(app)}")
    print(f"    - App name: {app.name}")
except Exception as e:
    print(f"    [FAILED] {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 5: Check WSGI handler
print("\n[5] Testing WSGI handler...")
try:
    import app as app_module
    print("    [OK] app module imported")
    print(f"    - Module has 'app' attribute: {hasattr(app_module, 'app')}")
    print(f"    - app_module.app type: {type(app_module.app)}")
    print(f"    - app_module.app is Flask app: {app_module.app is app}")
except Exception as e:
    print(f"    [FAILED] {e}")
    traceback.print_exc()

# Test 6: Check app routes
print("\n[6] Testing app routes...")
try:
    routes = list(app.url_map.iter_rules())
    print(f"    [OK] App has {len(routes)} routes")
    for rule in routes[:5]:  # Show first 5 routes
        print(f"    - {rule.rule} -> {rule.endpoint}")
    if len(routes) > 5:
        print(f"    ... and {len(routes) - 5} more routes")
except Exception as e:
    print(f"    [FAILED] {e}")
    traceback.print_exc()

# Test 7: Check for syntax errors in modified files
print("\n[7] Checking for syntax errors in modified files...")
files_to_check = ['app.py', 'database.py']
for filename in files_to_check:
    try:
        with open(filename, 'r') as f:
            compile(f.read(), filename, 'exec')
        print(f"    [OK] {filename} - no syntax errors")
    except SyntaxError as e:
        print(f"    [FAILED] {filename} - SYNTAX ERROR at line {e.lineno}: {e.msg}")

# Test 8: Test migration conversion
print("\n[8] Testing migration conversion...")
try:
    test_sql = "CREATE TABLE test (id INTEGER PRIMARY KEY AUTOINCREMENT, active INTEGER DEFAULT 0);"
    converted = db.convert_schema_for_postgres(test_sql)
    print("    [OK] Schema conversion works")
    print(f"    - Original: {test_sql}")
    print(f"    - Converted: {converted}")
except Exception as e:
    print(f"    [FAILED] {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNOSTICS COMPLETE")
print("=" * 60)
