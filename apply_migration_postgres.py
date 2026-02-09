#!/usr/bin/env python3
"""Apply migration directly to PostgreSQL database"""

import os
import re
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL
DATABASE_URL = os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: No DATABASE_URL or POSTGRES_URL found in environment")
    exit(1)

print(f"Connecting to PostgreSQL database...")
print(f"Database URL: {DATABASE_URL[:30]}...")

# Connect to database
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

print("\nReading migration file...")
with open('migrations/004_add_agents_teams.sql', 'r', encoding='utf-8') as f:
    migration_sql = f.read()

# PostgreSQL doesn't support AUTOINCREMENT, need to convert to SERIAL
print("\nConverting SQLite syntax to PostgreSQL...")
migration_sql = migration_sql.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
migration_sql = migration_sql.replace('TIMESTAMP DEFAULT CURRENT_TIMESTAMP', 'TIMESTAMP DEFAULT NOW()')
# PostgreSQL uses true/false for booleans, not 1/0
migration_sql = migration_sql.replace('BOOLEAN NOT NULL DEFAULT 1', 'BOOLEAN NOT NULL DEFAULT true')
migration_sql = migration_sql.replace('BOOLEAN NOT NULL DEFAULT 0', 'BOOLEAN NOT NULL DEFAULT false')
migration_sql = migration_sql.replace('BOOLEAN DEFAULT 1', 'BOOLEAN DEFAULT true')
migration_sql = migration_sql.replace('BOOLEAN DEFAULT 0', 'BOOLEAN DEFAULT false')

# Remove comments and split into statements
lines = []
for line in migration_sql.split('\n'):
    # Skip comment lines and rollback section
    if line.strip().startswith('--') or 'ROLLBACK SQL' in line:
        continue
    lines.append(line)

migration_sql = '\n'.join(lines)

# Split by semicolons and execute each statement
raw_statements = [s.strip() for s in migration_sql.split(';') if s.strip()]

# Categorize statements
create_table_statements = []
create_index_statements = []

for stmt in raw_statements:
    if 'CREATE TABLE' in stmt.upper():
        create_table_statements.append(stmt)
    elif 'CREATE INDEX' in stmt.upper():
        create_index_statements.append(stmt)

print(f"\nFound {len(create_table_statements)} CREATE TABLE statements")
print(f"Found {len(create_index_statements)} CREATE INDEX statements")

print("\nApplying migration...")

# Execute CREATE TABLE statements first
for i, statement in enumerate(create_table_statements, 1):
    try:
        print(f"  Creating table {i}/{len(create_table_statements)}...")
        cursor.execute(statement)
        conn.commit()
    except Exception as e:
        if 'already exists' in str(e):
            print(f"    -> Already exists, skipping")
        else:
            print(f"    -> Error: {e}")
            raise

# Then execute CREATE INDEX statements
for i, statement in enumerate(create_index_statements, 1):
    try:
        print(f"  Creating index {i}/{len(create_index_statements)}...")
        cursor.execute(statement)
        conn.commit()
    except Exception as e:
        if 'already exists' in str(e):
            print(f"    -> Already exists, skipping")
        else:
            print(f"    -> Error: {e}")
            raise

print("\n[PASS] Migration 004 applied successfully to PostgreSQL!")

# Verify tables were created
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('agents', 'teams', 'ratings')")
tables = cursor.fetchall()
print(f"\nVerifying tables created: {[t[0] for t in tables]}")

cursor.close()
conn.close()

print("\n[DONE] Migration complete!")
