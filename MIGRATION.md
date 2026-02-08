# Agent Modes Database - Migration Guide

Guide for applying database migrations and managing database schema changes.

## Table of Contents

1. [Overview](#overview)
2. [Migration Files](#migration-files)
3. [Applying Migrations](#applying-migrations)
4. [Migration Order](#migration-order)
5. [Rollback Procedures](#rollback-procedures)
6. [Troubleshooting](#troubleshooting)
7. [Creating New Migrations](#creating-new-migrations)

---

## Overview

The Agent Modes Database uses a migration system to manage database schema changes over time. Migrations are SQL scripts that modify the database structure to add new features, tables, or columns.

**Current Database Version:** 3.0

**Migration Files:**
- `001_add_file_upload_support.sql` - File upload tracking
- `002_add_format_conversions.sql` - Format conversion history
- `003_add_agent_cards.sql` - Agent card storage

---

## Migration Files

### Migration 001: Add File Upload Support

**File:** `migrations/001_add_file_upload_support.sql`

**Changes:**
- Creates `file_uploads` table to track uploaded files
- Adds columns to `agent_templates` table:
  - `source_format` - Track the source format (claude, roo, custom, manual)
  - `source_file_id` - Reference to the file upload
  - `is_imported` - Flag for imported templates
- Adds columns to `custom_agents` table:
  - `source_format` - Track the source format
  - `source_file_id` - Reference to the file upload
  - `is_imported` - Flag for imported agents

**Purpose:** Enable file upload functionality and track the origin of imported templates and agents.

### Migration 002: Add Format Conversions Support

**File:** `migrations/002_add_format_conversions.sql`

**Changes:**
- Creates `format_conversions` table to track conversion operations
- Adds indexes for efficient querying by source format, target format, and status

**Purpose:** Enable format conversion history tracking and audit trail.

### Migration 003: Add Agent Cards Support

**File:** `migrations/003_add_agent_cards.sql`

**Changes:**
- Creates `agent_cards` table to store generated agent cards
- Adds unique constraint on (entity_type, entity_id) to prevent duplicate cards
- Adds indexes for efficient querying

**Purpose:** Enable agent card generation and storage for Microsoft discoverability.

---

## Applying Migrations

### Automatic Migration

When you start the application for the first time, the database is automatically initialized with the latest schema. No manual migration is required.

```bash
python app.py
```

The application will:
1. Check if `agents.db` exists
2. If not, create the database with the full schema
3. Initialize seed data

### Manual Migration

If you're upgrading from an earlier version, you may need to apply migrations manually.

#### Option 1: Using Python

```bash
python -c "import database; database.apply_migrations()"
```

This will:
1. Check the current database schema
2. Apply any pending migrations in order
3. Update the database to the latest version

#### Option 2: Using SQLite Command Line

```bash
# Navigate to the project directory
cd agent-modes-db

# Open the database
sqlite3 agents.db

# Apply migrations in order
.read migrations/001_add_file_upload_support.sql
.read migrations/002_add_format_conversions.sql
.read migrations/003_add_agent_cards.sql

# Exit SQLite
.exit
```

#### Option 3: Using a Database Tool

You can use any SQLite database tool (DB Browser for SQLite, DBeaver, etc.) to:
1. Open `agents.db`
2. Execute each migration SQL file in order
3. Commit the changes

### Checking Migration Status

To check which migrations have been applied:

```bash
sqlite3 agents.db "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
```

Expected tables (after all migrations):
- `agent_templates`
- `agent_configurations`
- `custom_agents`
- `file_uploads`
- `format_conversions`
- `agent_cards`

---

## Migration Order

Migrations must be applied in the following order:

1. **001_add_file_upload_support.sql** - Adds file upload tracking
2. **002_add_format_conversions.sql** - Adds conversion history
3. **003_add_agent_cards.sql** - Adds agent card storage

**Important:** Do not skip migrations or apply them out of order, as later migrations may depend on tables or columns created by earlier migrations.

### Why Order Matters

- Migration 001 creates the `file_uploads` table
- Migration 002 creates the `format_conversions` table
- Migration 003 creates the `agent_cards` table

Each migration is independent, but they represent the chronological evolution of the database schema.

---

## Rollback Procedures

### Warning: Rollbacks Are Destructive

Rolling back a migration will:
- Delete tables created by the migration
- Remove columns added by the migration
- **Permanently delete all data** in those tables/columns

**Always backup your database before rolling back!**

### Backup Before Rollback

```bash
# Create a backup
cp agents.db agents.db.backup.$(date +%Y%m%d_%H%M%S)
```

### Rollback Migration 003

To rollback migration 003 (Agent Cards):

```bash
sqlite3 agents.db <<EOF
DROP INDEX IF EXISTS idx_agent_cards_published;
DROP INDEX IF EXISTS idx_agent_cards_entity;
DROP TABLE IF EXISTS agent_cards;
EOF
```

This will:
- Delete the `agent_cards` table
- Delete all agent card data
- Remove indexes

### Rollback Migration 002

To rollback migration 002 (Format Conversions):

```bash
sqlite3 agents.db <<EOF
DROP INDEX IF EXISTS idx_conversions_status;
DROP INDEX IF EXISTS idx_conversions_target;
DROP INDEX IF EXISTS idx_conversions_source;
DROP TABLE IF EXISTS format_conversions;
EOF
```

This will:
- Delete the `format_conversions` table
- Delete all conversion history
- Remove indexes

### Rollback Migration 001

To rollback migration 001 (File Upload Support):

```bash
sqlite3 agents.db <<EOF
DROP INDEX IF EXISTS idx_custom_agents_source_file;
DROP INDEX IF EXISTS idx_templates_source_file;
-- Note: SQLite doesn't support DROP COLUMN, so we need to recreate tables
-- This is complex and may require manual intervention
EOF
```

**Note:** Rolling back Migration 001 is complex because SQLite doesn't support dropping columns. You may need to:
1. Export data from `agent_templates` and `custom_agents`
2. Drop and recreate these tables without the new columns
3. Re-import the data
4. Re-create indexes

**Recommendation:** If you need to rollback Migration 001, consider starting fresh with a new database instead.

### Rollback All Migrations

To rollback all migrations and start fresh:

```bash
# Stop the application
# Backup the database
cp agents.db agents.db.backup

# Delete the database
rm agents.db

# Restart the application
python app.py
```

This will create a fresh database with the original schema (before any migrations).

---

## Troubleshooting

### Migration Fails with "Table Already Exists"

**Problem:** Migration fails because a table already exists.

**Solution:**
- Check if the migration was already applied
- Verify the current schema
- If the table exists and has the correct structure, you can skip this migration

```bash
# Check if table exists
sqlite3 agents.db "SELECT name FROM sqlite_master WHERE type='table' AND name='file_uploads';"
```

### Migration Fails with "Column Already Exists"

**Problem:** Migration fails because a column already exists.

**Solution:**
- SQLite doesn't support `IF NOT EXISTS` for `ALTER TABLE ADD COLUMN`
- Check if the column exists before attempting to add it
- If the column exists, you can skip the ALTER TABLE statement

```bash
# Check if column exists
sqlite3 agents.db "PRAGMA table_info(agent_templates);"
```

### Migration Fails with "Foreign Key Constraint"

**Problem:** Migration fails due to foreign key constraints.

**Solution:**
- Ensure referenced tables exist
- Check that referenced columns exist
- Verify data integrity before applying migration

```bash
# Check foreign key constraints
sqlite3 agents.db "PRAGMA foreign_keys;"
```

### Database Locked

**Problem:** Migration fails with "database is locked" error.

**Solution:**
- Ensure the application is not running
- Close all database connections
- Check for other processes accessing the database

```bash
# Stop the application
# Check for SQLite processes
ps aux | grep sqlite

# Try again
python -c "import database; database.apply_migrations()"
```

### Migration Applied Partially

**Problem:** Migration was applied partially and failed partway through.

**Solution:**
- Check the current state of the database
- Manually complete the remaining steps
- Or rollback and re-apply the migration

```bash
# Check current schema
sqlite3 agents.db ".schema"

# Manually execute remaining SQL statements
sqlite3 agents.db "ALTER TABLE agent_templates ADD COLUMN IF NOT EXISTS source_format TEXT;"
```

### Data Loss After Migration

**Problem:** Data is missing after applying a migration.

**Solution:**
- Restore from backup if available
- Check migration SQL for data loss operations
- Review migration logs

```bash
# Restore from backup
cp agents.db.backup.20240101_120000 agents.db
```

### Performance Issues After Migration

**Problem:** Database is slow after applying migrations.

**Solution:**
- Run `VACUUM` to optimize the database
- Run `ANALYZE` to update statistics
- Check that indexes were created

```bash
# Optimize database
sqlite3 agents.db "VACUUM;"
sqlite3 agents.db "ANALYZE;"
```

---

## Creating New Migrations

When adding new features that require database changes:

### 1. Create Migration File

Create a new SQL file in the `migrations/` directory:

```bash
# Use sequential numbering
touch migrations/004_new_feature.sql
```

### 2. Write Migration SQL

Include both forward and rollback SQL:

```sql
-- Migration 004: Add New Feature
-- Description: Add support for new feature

-- ============================================
-- FORWARD MIGRATION
-- ============================================

-- Create new table
CREATE TABLE IF NOT EXISTS new_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add new column to existing table
ALTER TABLE existing_table ADD COLUMN new_column TEXT;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_new_table_name ON new_table(name);

-- ============================================
-- ROLLBACK SQL (for reference only)
-- ============================================
-- DROP INDEX IF EXISTS idx_new_table_name;
-- DROP TABLE IF EXISTS new_table;
-- Note: SQLite doesn't support DROP COLUMN, so column rollback requires table recreation
```

### 3. Update Database Functions

Add new functions in `database.py` to work with the new table/columns:

```python
def create_new_feature(name):
    """Create a new feature entry"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO new_table (name) VALUES (?)",
        (name,)
    )
    conn.commit()
    conn.close()
    return cursor.lastrowid
```

### 4. Update Schema File

Keep `schema.sql` in sync with migrations:

```sql
-- Add new table definition
CREATE TABLE IF NOT EXISTS new_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add new column to existing table
ALTER TABLE existing_table ADD COLUMN new_column TEXT;
```

### 5. Test Migration

Test the migration on a copy of the database:

```bash
# Create test database
cp agents.db agents.test.db

# Apply migration to test database
sqlite3 agents.test.db < migrations/004_new_feature.sql

# Verify migration
sqlite3 agents.test.db ".schema"

# Test application with test database
# (modify database path in code temporarily)
```

### 6. Document Migration

Update this file with details about the new migration:

```markdown
### Migration 004: Add New Feature

**File:** `migrations/004_new_feature.sql`

**Changes:**
- Creates `new_table` table
- Adds `new_column` to `existing_table`

**Purpose:** Enable new feature functionality.
```

### 7. Update Application Code

Update `app.py` to use new database functions:

```python
@app.route('/api/new-feature', methods=['POST'])
def create_new_feature():
    data = request.get_json()
    feature_id = db.create_new_feature(data['name'])
    return jsonify({'id': feature_id, 'message': 'Feature created successfully'}), 201
```

### 8. Update Documentation

Update relevant documentation files:
- Update API.md with new endpoints
- Update USER_GUIDE.md with new features
- Update ARCHITECTURE.md with schema changes
- Update CONTRIBUTING.md with migration instructions

---

## Best Practices

### Migration Development

1. **Test thoroughly** - Always test migrations on a copy of the database
2. **Backup first** - Always create a backup before applying migrations
3. **Document clearly** - Include comments explaining what each migration does
4. **Keep it atomic** - Each migration should be a single, atomic change
5. **Consider rollback** - Always include rollback SQL for reference

### Migration Application

1. **Apply in order** - Never skip migrations or apply out of order
2. **Verify after applying** - Check that the migration was applied correctly
3. **Test the application** - Ensure the application works after migration
4. **Monitor for issues** - Watch for errors or performance issues

### Production Deployment

1. **Schedule downtime** - Plan for application downtime during migration
2. **Backup production database** - Always backup before production migration
3. **Test on staging** - Test migrations on a staging environment first
4. **Have rollback plan** - Know how to rollback if something goes wrong
5. **Monitor closely** - Watch for issues after deployment

---

## Migration Checklist

Before applying a migration:

- [ ] Read the migration file and understand what it does
- [ ] Backup the database
- [ ] Test migration on a copy of the database
- [ ] Review rollback procedure
- [ ] Schedule appropriate downtime
- [ ] Notify users of planned maintenance

After applying a migration:

- [ ] Verify migration was applied successfully
- [ ] Check database schema
- [ ] Test the application
- [ ] Verify data integrity
- [ ] Monitor for errors
- [ ] Update documentation
- [ ] Communicate changes to users

---

## Support

If you encounter issues with migrations:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the migration SQL file for errors
3. Check the database schema with `sqlite3 agents.db ".schema"`
4. Open an issue on GitHub with:
   - Migration number
   - Error message
   - Current database schema
   - Steps to reproduce

---

## Additional Resources

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Database Functions](database.py) - Database operation functions
- [Schema File](schema.sql) - Complete database schema
- [Architecture Documentation](ARCHITECTURE.md) - System design and architecture
- [API Documentation](API.md) - API endpoint reference
- [Contributing Guide](CONTRIBUTING.md) - Development guidelines
