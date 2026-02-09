import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager

# Check if Postgres connection info is available
POSTGRES_URL = os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL')
USE_POSTGRES = bool(POSTGRES_URL)

# Determine database file path based on environment (only for SQLite)
# On Vercel serverless functions, only /tmp is writable
if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
    # WARNING: /tmp is ephemeral on Vercel serverless functions
    # Data will be lost between cold starts. Use PostgreSQL for persistence.
    # SQLite also has concurrency issues under load.
    DB_FILE = '/tmp/modes.db'
else:
    DB_FILE = 'agents.db'

# Import psycopg2 only if Postgres is available
if USE_POSTGRES:
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        from psycopg2 import sql
        POSTGRES_AVAILABLE = True
    except ImportError:
        print("Warning: psycopg2 not installed, falling back to SQLite")
        USE_POSTGRES = False
        POSTGRES_AVAILABLE = False
else:
    POSTGRES_AVAILABLE = False

# Database type constants
DB_TYPE_POSTGRES = 'postgres'
DB_TYPE_SQLITE = 'sqlite'

def get_db_type():
    """Get the current database type being used"""
    return DB_TYPE_POSTGRES if USE_POSTGRES else DB_TYPE_SQLITE

def get_placeholder():
    """Get the appropriate placeholder for the current database"""
    return '%s' if USE_POSTGRES else '?'

def convert_bool(value):
    """Convert boolean to appropriate database value"""
    if USE_POSTGRES:
        # Postgres handles booleans natively
        return value
    else:
        # SQLite uses 0/1 for booleans
        return 1 if value else 0

def parse_bool(value):
    """Parse boolean from database value"""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    return bool(value)

@contextmanager
def get_db():
    """Context manager for database connections"""
    if USE_POSTGRES and POSTGRES_AVAILABLE:
        conn = psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

def get_last_insert_id(conn, cursor):
    """Get the last inserted ID for the current database type"""
    if USE_POSTGRES:
        # For Postgres, we need to use RETURNING clause or fetch from cursor
        # This is handled by using RETURNING in INSERT statements
        # For backward compatibility, we'll try to get the OID
        # Note: This is not reliable for all cases, so prefer RETURNING
        return cursor.lastrowid if hasattr(cursor, 'lastrowid') else None
    else:
        return cursor.lastrowid

def execute_insert(conn, query, params):
    """Execute an INSERT query and return the inserted ID"""
    cursor = conn.cursor()
    
    if USE_POSTGRES:
        # For Postgres, add RETURNING clause to get the ID
        if 'RETURNING' not in query.upper():
            # Extract the table name from the INSERT statement
            query_upper = query.upper()
            into_pos = query_upper.find('INTO ') + 5
            values_pos = query_upper.find(' VALUES')
            table_name = query[into_pos:values_pos].strip()
            
            # Add RETURNING id clause
            query = query.rstrip(';') + ' RETURNING id;'
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        if result:
            return result['id']
    else:
        cursor.execute(query, params)
        return cursor.lastrowid
    
    return None

def execute_query(conn, query, params=None):
    """
    Execute a SELECT query and return results.
    Works for both SQLite and Postgres.

    Args:
        conn: Database connection
        query: SQL query string
        params: Query parameters (optional)

    Returns:
        Result of fetchall() for SELECT queries
    """
    if USE_POSTGRES:
        # Explicitly pass RealDictCursor to ensure dict-like rows
        from psycopg2.extras import RealDictCursor
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params or ())
        return cursor.fetchall()
    else:
        if params:
            return conn.execute(query, params).fetchall()
        else:
            return conn.execute(query).fetchall()

def execute_query_one(conn, query, params=None):
    """
    Execute a SELECT query and return a single result.
    Works for both SQLite and Postgres.
    
    Args:
        conn: Database connection
        query: SQL query string
        params: Query parameters (optional)
    
    Returns:
        Result of fetchone() for SELECT queries
    """
    if USE_POSTGRES:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        return cursor.fetchone()
    else:
        if params:
            return conn.execute(query, params).fetchone()
        else:
            return conn.execute(query).fetchone()

def execute_update(conn, query, params=None):
    """
    Execute an INSERT/UPDATE/DELETE query.
    Works for both SQLite and Postgres.
    
    Args:
        conn: Database connection
        query: SQL query string
        params: Query parameters (optional)
    """
    if USE_POSTGRES:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
    else:
        if params:
            conn.execute(query, params)
        else:
            conn.execute(query)

def tables_exist():
    """Check if database tables already exist"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            if USE_POSTGRES:
                # Check if agent_templates table exists in PostgreSQL
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'agent_templates'
                    );
                """)
                result = cursor.fetchone()
                return result['exists'] if result else False
            else:
                # Check if agent_templates table exists in SQLite
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='agent_templates';
                """)
                return cursor.fetchone() is not None
    except Exception as e:
        # If it's a connection error, we should fail fast and make it clear
        error_msg = str(e).lower()
        if 'connection' in error_msg or 'connect' in error_msg:
            print(f"Database connection error: {e}")
            raise  # Re-raise connection errors
        print(f"Error checking if tables exist: {e}")
        return False  # For other errors, assume tables don't exist

def init_db():
    """Initialize database with schema and apply all migrations"""
    # Skip initialization if tables already exist (prevents re-init on every cold start)
    if tables_exist():
        print("Database tables already exist, skipping initialization")
        return

    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r') as f:
        schema = f.read()

    # Convert schema for Postgres if needed
    if USE_POSTGRES:
        schema = convert_schema_for_postgres(schema)

    with get_db() as conn:
        if USE_POSTGRES:
            # For Postgres, execute each statement separately
            execute_sql_script(conn, schema)
        else:
            # For SQLite, use executescript
            conn.executescript(schema)

    # Apply all migrations in order
    migrations = [
        '001_add_file_upload_support.sql',
        '002_add_format_conversions.sql',
        '003_add_agent_cards.sql'
    ]
    
    for migration_file in migrations:
        try:
            apply_migration(migration_file)
        except Exception as e:
            print(f"Warning: Failed to apply migration {migration_file}: {e}")

    # Add seed data
    seed_builtin_templates()

def execute_sql_script(conn, script):
    """
    Execute a SQL script with multiple statements (for Postgres)
    
    Args:
        conn: Database connection
        script: SQL script with multiple statements
    """
    cursor = conn.cursor()
    
    # Split the script into individual statements
    # Remove comments and empty lines
    statements = []
    current_statement = []
    
    for line in script.split('\n'):
        # Skip comments
        stripped_line = line.strip()
        if stripped_line.startswith('--'):
            continue
        
        current_statement.append(line)
        
        # Check if the line ends with a semicolon (end of statement)
        if stripped_line.endswith(';'):
            statement = '\n'.join(current_statement).strip()
            if statement:
                statements.append(statement)
            current_statement = []
    
    # Execute each statement
    for statement in statements:
        try:
            cursor.execute(statement)
        except Exception as e:
            # Ignore errors for statements that already exist (e.g., CREATE TABLE IF NOT EXISTS)
            if 'already exists' in str(e).lower():
                continue
            raise e

def convert_schema_for_postgres(schema):
    """Convert SQLite schema to Postgres-compatible schema"""
    # Replace AUTOINCREMENT with SERIAL
    schema = schema.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
    
    # Replace BOOLEAN with BOOLEAN (same in both, but ensure proper handling)
    # SQLite doesn't have native BOOLEAN, but we handle it in Python
    
    # Replace CURRENT_TIMESTAMP with CURRENT_TIMESTAMP (same in both)
    
    # Replace boolean default values: DEFAULT 0 -> DEFAULT FALSE, DEFAULT 1 -> DEFAULT TRUE
    # Postgres requires boolean literals (FALSE/TRUE) instead of integers (0/1) for boolean columns
    import re
    schema = re.sub(r'DEFAULT\s+0\b', 'DEFAULT FALSE', schema)
    schema = re.sub(r'DEFAULT\s+1\b', 'DEFAULT TRUE', schema)
    
    # Replace ? with %s for parameter placeholders
    # Note: This is a simple replacement and may not work for all cases
    # Better to use parameterized queries in the actual code
    
    return schema

def apply_migration(migration_file):
    """
    Apply a database migration script
    
    Args:
        migration_file: Path to the migration SQL file
    
    Returns:
        bool: True if migration was applied successfully
    """
    migration_path = os.path.join(os.path.dirname(__file__), 'migrations', migration_file)
    if not os.path.exists(migration_path):
        raise FileNotFoundError(f"Migration file not found: {migration_path}")
    
    with open(migration_path, 'r') as f:
        migration_sql = f.read()
    
    # Convert migration for Postgres if needed
    if USE_POSTGRES:
        migration_sql = convert_migration_for_postgres(migration_sql)
    
    with get_db() as conn:
        try:
            if USE_POSTGRES:
                # For Postgres, execute each statement separately
                execute_sql_script(conn, migration_sql)
            else:
                # For SQLite, use executescript
                conn.executescript(migration_sql)
            return True
        except Exception as e:
            # If error is about duplicate column, it's already migrated (idempotent)
            if 'duplicate column' in str(e).lower() or 'column' in str(e).lower() and 'already exists' in str(e).lower():
                return True
            raise e

def convert_migration_for_postgres(migration_sql):
    """Convert SQLite migration to Postgres-compatible migration"""
    # Replace AUTOINCREMENT with SERIAL
    migration_sql = migration_sql.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
    
    # Replace boolean default values: DEFAULT 0 -> DEFAULT FALSE, DEFAULT 1 -> DEFAULT TRUE
    # Postgres requires boolean literals (FALSE/TRUE) instead of integers (0/1) for boolean columns
    import re
    migration_sql = re.sub(r'DEFAULT\s+0\b', 'DEFAULT FALSE', migration_sql)
    migration_sql = re.sub(r'DEFAULT\s+1\b', 'DEFAULT TRUE', migration_sql)
    
    # Handle ALTER TABLE ADD COLUMN for Postgres
    # Postgres doesn't support IF NOT EXISTS for ADD COLUMN
    # The execute_sql_script function handles idempotency with try-catch
    
    return migration_sql

def seed_builtin_templates():
    """Add example builtin templates"""
    templates = [
        {
            'name': 'Code Explorer',
            'description': 'Specialized agent for exploring and understanding codebases. Can search, analyze, and explain code structure.',
            'category': 'Development',
            'is_builtin': True
        },
        {
            'name': 'Test Runner',
            'description': 'Agent focused on running tests, analyzing test results, and debugging test failures.',
            'category': 'Testing',
            'is_builtin': True
        },
        {
            'name': 'Documentation Generator',
            'description': 'Creates comprehensive documentation from code, including API docs, README files, and inline comments.',
            'category': 'Documentation',
            'is_builtin': True
        },
        {
            'name': 'Bug Fixer',
            'description': 'Identifies, analyzes, and fixes bugs in code. Can trace issues and propose solutions.',
            'category': 'Development',
            'is_builtin': True
        },
        {
            'name': 'Code Reviewer',
            'description': 'Reviews code for quality, style, security issues, and best practices.',
            'category': 'Development',
            'is_builtin': True
        }
    ]

    with get_db() as conn:
        for template in templates:
            # Check if template already exists
            query = 'SELECT id FROM agent_templates WHERE name = %s AND is_builtin = %s' if USE_POSTGRES else 'SELECT id FROM agent_templates WHERE name = ? AND is_builtin = 1'
            params = (template['name'], convert_bool(True)) if USE_POSTGRES else (template['name'],)
            existing = execute_query_one(conn, query, params)

            if not existing:
                query = '''INSERT INTO agent_templates (name, description, category, is_builtin)
                           VALUES (%s, %s, %s, %s)''' if USE_POSTGRES else \
                       '''INSERT INTO agent_templates (name, description, category, is_builtin)
                          VALUES (?, ?, ?, ?)'''
                params = (template['name'], template['description'], template['category'], convert_bool(True)) if USE_POSTGRES else \
                        (template['name'], template['description'], template['category'], template['is_builtin'])
                execute_update(conn, query, params)

# Agent Templates CRUD
def get_all_templates():
    """Get all agent templates"""
    with get_db() as conn:
        rows = execute_query(conn, 'SELECT * FROM agent_templates ORDER BY is_builtin DESC, name ASC')
        return [dict(row) for row in rows]

def get_template_by_id(template_id):
    """Get specific template by ID"""
    with get_db() as conn:
        query = 'SELECT * FROM agent_templates WHERE id = %s' if USE_POSTGRES else 'SELECT * FROM agent_templates WHERE id = ?'
        row = execute_query_one(conn, query, (template_id,))
        return dict(row) if row else None

def create_template(name, description, category, is_builtin=False, source_format=None, source_file_id=None, is_imported=False):
    """
    Create new agent template
    
    Args:
        name: Template name
        description: Template description
        category: Template category
        is_builtin: Whether this is a builtin template
        source_format: Source format ('claude', 'roo', 'custom', 'manual')
        source_file_id: ID of the source file upload
        is_imported: Whether this was imported from a file
    
    Returns:
        int: The ID of the created template
    """
    with get_db() as conn:
        if USE_POSTGRES:
            query = '''INSERT INTO agent_templates (name, description, category, is_builtin, source_format, source_file_id, is_imported)
                       VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id'''
            params = (name, description, category, convert_bool(is_builtin), source_format, source_file_id, convert_bool(is_imported))
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            template_id = result['id']
        else:
            query = '''INSERT INTO agent_templates (name, description, category, is_builtin, source_format, source_file_id, is_imported)
                       VALUES (?, ?, ?, ?, ?, ?, ?)'''
            params = (name, description, category, is_builtin, source_format, source_file_id, is_imported)
            cursor = conn.cursor()
            cursor.execute(query, params)
            template_id = cursor.lastrowid
    
    # Auto-generate agent card for the new template
    # _generate_and_store_agent_card("template", template_id)    
    return template_id

def update_template(template_id, name, description, category, source_format=None, source_file_id=None, is_imported=None):
    """
    Update existing template
    
    Args:
        template_id: Template ID to update
        name: New template name
        description: New template description
        category: New template category
        source_format: New source format (optional)
        source_file_id: New source file ID (optional)
        is_imported: New is_imported value (optional)
    
    Returns:
        int: The ID of the updated template
    """
    with get_db() as conn:
        # Build dynamic update query based on provided parameters
        ph = '%s' if USE_POSTGRES else '?'
        update_fields = [f'name = {ph}', f'description = {ph}', f'category = {ph}', 'updated_at = CURRENT_TIMESTAMP']
        params = [name, description, category]
        
        if source_format is not None:
            update_fields.append(f'source_format = {ph}')
            params.append(source_format)
        
        if source_file_id is not None:
            update_fields.append(f'source_file_id = {ph}')
            params.append(source_file_id)
        
        if is_imported is not None:
            update_fields.append(f'is_imported = {ph}')
            params.append(convert_bool(is_imported) if USE_POSTGRES else is_imported)
        
        params.append(template_id)
        
        query = f"UPDATE agent_templates SET {', '.join(update_fields)} WHERE id = {ph}"
        execute_update(conn, query, params)
    
    # Auto-regenerate agent card for the updated template
    _generate_and_store_agent_card('template', template_id)
    # _generate_and_store_agent_card("template", template_id)
    return template_id

def delete_template(template_id):
    """Delete template (only if not builtin)"""
    with get_db() as conn:
        # Check if builtin
        ph = '%s' if USE_POSTGRES else '?'
        row = execute_query_one(conn, f'SELECT is_builtin FROM agent_templates WHERE id = {ph}', (template_id,))

        if row and parse_bool(row['is_builtin']):
            raise ValueError("Cannot delete builtin templates")

        execute_update(conn, f'DELETE FROM agent_templates WHERE id = {ph}', (template_id,))
        return True

# Agent Configurations CRUD
def get_all_configurations():
    """Get all agent configurations with template info"""
    with get_db() as conn:
        rows = execute_query(conn, '''SELECT c.*, t.name as template_name
               FROM agent_configurations c
               LEFT JOIN agent_templates t ON c.template_id = t.id
               ORDER BY c.updated_at DESC''')
        return [dict(row) for row in rows]

def get_configuration_by_id(config_id):
    """Get specific configuration by ID"""
    with get_db() as conn:
        ph = '%s' if USE_POSTGRES else '?'
        row = execute_query_one(conn, f'''SELECT c.*, t.name as template_name
               FROM agent_configurations c
               LEFT JOIN agent_templates t ON c.template_id = t.id
               WHERE c.id = {ph}''', (config_id,))
        return dict(row) if row else None

def create_configuration(name, template_id, config_json):
    """Create new agent configuration"""
    with get_db() as conn:
        if USE_POSTGRES:
            query = '''INSERT INTO agent_configurations (name, template_id, config_json)
                       VALUES (%s, %s, %s) RETURNING id'''
            params = (name, template_id, json.dumps(config_json) if isinstance(config_json, dict) else config_json)
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            config_id = result['id']
        else:
            query = '''INSERT INTO agent_configurations (name, template_id, config_json)
                       VALUES (?, ?, ?)'''
            params = (name, template_id, json.dumps(config_json) if isinstance(config_json, dict) else config_json)
            cursor = conn.cursor()
            cursor.execute(query, params)
            config_id = cursor.lastrowid
    
    # Auto-generate agent card for the new configuration
    _generate_and_store_agent_card('configuration', config_id)
    
    return config_id

def update_configuration(config_id, name, template_id, config_json):
    """Update existing configuration"""
    with get_db() as conn:
        ph = '%s' if USE_POSTGRES else '?'
        execute_update(conn, f'''UPDATE agent_configurations
               SET name = {ph}, template_id = {ph}, config_json = {ph}, updated_at = CURRENT_TIMESTAMP
               WHERE id = {ph}''',
            (name, template_id, json.dumps(config_json) if isinstance(config_json, dict) else config_json, config_id)
        )
    
    # Auto-regenerate agent card for the updated configuration
    _generate_and_store_agent_card('configuration', config_id)
    
    return config_id

def delete_configuration(config_id):
    """Delete configuration"""
    with get_db() as conn:
        ph = '%s' if USE_POSTGRES else '?'
        execute_update(conn, f'DELETE FROM agent_configurations WHERE id = {ph}', (config_id,))
        return True

# Custom Agents CRUD
def get_all_custom_agents():
    """Get all custom agents"""
    with get_db() as conn:
        rows = execute_query(conn, 'SELECT * FROM custom_agents ORDER BY updated_at DESC')
        return [dict(row) for row in rows]

def get_custom_agent_by_id(agent_id):
    """Get specific custom agent by ID"""
    with get_db() as conn:
        ph = '%s' if USE_POSTGRES else '?'
        row = execute_query_one(conn, f'SELECT * FROM custom_agents WHERE id = {ph}', (agent_id,))
        return dict(row) if row else None

def create_custom_agent(name, description, capabilities, tools, system_prompt, config_schema=None, source_format=None, source_file_id=None, is_imported=False):
    """
    Create new custom agent
    
    Args:
        name: Agent name
        description: Agent description
        capabilities: List of capabilities
        tools: List of tools
        system_prompt: System prompt
        config_schema: Optional configuration schema
        source_format: Source format ('claude', 'roo', 'custom', 'manual')
        source_file_id: ID of the source file upload
        is_imported: Whether this was imported from a file
    
    Returns:
        int: The ID of the created agent
    """
    with get_db() as conn:
        if USE_POSTGRES:
            query = '''INSERT INTO custom_agents (name, description, capabilities, tools, system_prompt, config_schema, source_format, source_file_id, is_imported)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id'''
            params = (
                name,
                description,
                json.dumps(capabilities) if isinstance(capabilities, list) else capabilities,
                json.dumps(tools) if isinstance(tools, list) else tools,
                system_prompt,
                json.dumps(config_schema) if config_schema and isinstance(config_schema, dict) else config_schema,
                source_format,
                source_file_id,
                convert_bool(is_imported)
            )
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            agent_id = result['id']
        else:
            query = '''INSERT INTO custom_agents (name, description, capabilities, tools, system_prompt, config_schema, source_format, source_file_id, is_imported)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            params = (
                name,
                description,
                json.dumps(capabilities) if isinstance(capabilities, list) else capabilities,
                json.dumps(tools) if isinstance(tools, list) else tools,
                system_prompt,
                json.dumps(config_schema) if config_schema and isinstance(config_schema, dict) else config_schema,
                source_format,
                source_file_id,
                is_imported
            )
            cursor = conn.cursor()
            cursor.execute(query, params)
            agent_id = cursor.lastrowid
    
    # Auto-generate agent card for the new custom agent
    _generate_and_store_agent_card('custom_agent', agent_id)
    
    return agent_id

def update_custom_agent(agent_id, name, description, capabilities, tools, system_prompt, config_schema=None, source_format=None, source_file_id=None, is_imported=None):
    """
    Update existing custom agent
    
    Args:
        agent_id: Agent ID to update
        name: New agent name
        description: New agent description
        capabilities: New capabilities list
        tools: New tools list
        system_prompt: New system prompt
        config_schema: New configuration schema (optional)
        source_format: New source format (optional)
        source_file_id: New source file ID (optional)
        is_imported: New is_imported value (optional)
    
    Returns:
        int: The ID of the updated agent
    """
    with get_db() as conn:
        # Build dynamic update query based on provided parameters
        ph = '%s' if USE_POSTGRES else '?'
        update_fields = [f'name = {ph}', f'description = {ph}', f'capabilities = {ph}', f'tools = {ph}',
                        f'system_prompt = {ph}', 'updated_at = CURRENT_TIMESTAMP']
        params = [
            name,
            description,
            json.dumps(capabilities) if isinstance(capabilities, list) else capabilities,
            json.dumps(tools) if isinstance(tools, list) else tools,
            system_prompt
        ]
        
        if config_schema is not None:
            update_fields.append(f'config_schema = {ph}')
            params.append(json.dumps(config_schema) if isinstance(config_schema, dict) else config_schema)
        
        if source_format is not None:
            update_fields.append(f'source_format = {ph}')
            params.append(source_format)
        
        if source_file_id is not None:
            update_fields.append(f'source_file_id = {ph}')
            params.append(source_file_id)
        
        if is_imported is not None:
            update_fields.append(f'is_imported = {ph}')
            params.append(convert_bool(is_imported) if USE_POSTGRES else is_imported)
        
        params.append(agent_id)
        
        query = f"UPDATE custom_agents SET {', '.join(update_fields)} WHERE id = {ph}"
        execute_update(conn, query, params)
    
    # Auto-regenerate agent card for the updated custom agent
    _generate_and_store_agent_card('custom_agent', agent_id)
    
    return agent_id

def delete_custom_agent(agent_id):
    """Delete custom agent"""
    with get_db() as conn:
        ph = '%s' if USE_POSTGRES else '?'
        execute_update(conn, f'DELETE FROM custom_agents WHERE id = {ph}', (agent_id,))
        return True

# File Uploads CRUD
def create_file_upload(filename, original_filename, file_format, file_size, upload_status='pending', parse_result=None, error_message=None):
    """
    Create a new file upload record
    
    Args:
        filename: Stored filename
        original_filename: Original filename from upload
        file_format: File format ('yaml', 'json', 'md')
        file_size: File size in bytes
        upload_status: Upload status ('pending', 'processing', 'completed', 'failed')
        parse_result: Parsed data as JSON string (optional)
        error_message: Error message if parsing failed (optional)
    
    Returns:
        int: The ID of the created file upload
    """
    with get_db() as conn:
        parse_result_json = json.dumps(parse_result) if parse_result and not isinstance(parse_result, str) else parse_result
        if USE_POSTGRES:
            query = '''INSERT INTO file_uploads (filename, original_filename, file_format, file_size, upload_status, parse_result, error_message)
                       VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id'''
            params = (filename, original_filename, file_format, file_size, upload_status, parse_result_json, error_message)
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result['id']
        else:
            query = '''INSERT INTO file_uploads (filename, original_filename, file_format, file_size, upload_status, parse_result, error_message)
                       VALUES (?, ?, ?, ?, ?, ?, ?)'''
            params = (filename, original_filename, file_format, file_size, upload_status, parse_result_json, error_message)
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid

def get_file_upload_by_id(upload_id):
    """
    Get specific file upload by ID
    
    Args:
        upload_id: File upload ID
    
    Returns:
        dict: File upload data or None if not found
    """
    with get_db() as conn:
        ph = '%s' if USE_POSTGRES else '?'
        row = execute_query_one(conn, f'SELECT * FROM file_uploads WHERE id = {ph}', (upload_id,))
        return dict(row) if row else None

def get_all_file_uploads(status=None, file_format=None):
    """
    Get all file uploads with optional filtering
    
    Args:
        status: Filter by upload status (optional)
        file_format: Filter by file format (optional)
    
    Returns:
        list: List of file upload dictionaries
    """
    with get_db() as conn:
        query = 'SELECT * FROM file_uploads'
        params = []
        
        if status or file_format:
            conditions = []
            ph = '%s' if USE_POSTGRES else '?'
            if status:
                conditions.append(f'upload_status = {ph}')
                params.append(status)
            if file_format:
                conditions.append(f'file_format = {ph}')
                params.append(file_format)
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY uploaded_at DESC'
        
        rows = execute_query(conn, query, params)
        return [dict(row) for row in rows]

def update_file_upload(upload_id, upload_status=None, parse_result=None, error_message=None):
    """
    Update a file upload record
    
    Args:
        upload_id: File upload ID to update
        upload_status: New upload status (optional)
        parse_result: New parse result (optional)
        error_message: New error message (optional)
    
    Returns:
        bool: True if update was successful
    """
    with get_db() as conn:
        update_fields = []
        params = []
        ph = '%s' if USE_POSTGRES else '?'
        
        if upload_status is not None:
            update_fields.append(f'upload_status = {ph}')
            params.append(upload_status)
            if upload_status in ['completed', 'failed']:
                update_fields.append('processed_at = CURRENT_TIMESTAMP')
        
        if parse_result is not None:
            parse_result_json = json.dumps(parse_result) if parse_result and not isinstance(parse_result, str) else parse_result
            update_fields.append(f'parse_result = {ph}')
            params.append(parse_result_json)
        
        if error_message is not None:
            update_fields.append(f'error_message = {ph}')
            params.append(error_message)
        
        if not update_fields:
            return True
        
        params.append(upload_id)
        query = f"UPDATE file_uploads SET {', '.join(update_fields)} WHERE id = {ph}"
        execute_update(conn, query, params)
        return True

def delete_file_upload(upload_id):
    """
    Delete a file upload record
    
    Args:
        upload_id: File upload ID to delete
    
    Returns:
        bool: True if deletion was successful
    """
    with get_db() as conn:
        ph = '%s' if USE_POSTGRES else '?'
        execute_update(conn, f'DELETE FROM file_uploads WHERE id = {ph}', (upload_id,))
        return True

# Format Conversions CRUD
def create_format_conversion(source_format, target_format, source_data, target_data, conversion_status='success', error_message=None):
    """
    Create a new format conversion record
    
    Args:
        source_format: Source format ('claude', 'roo', 'custom')
        target_format: Target format ('claude', 'roo', 'custom')
        source_data: Source data as dictionary
        target_data: Target data as dictionary
        conversion_status: Conversion status ('success', 'failed')
        error_message: Error message if conversion failed (optional)
    
    Returns:
        int: The ID of the created conversion record
    """
    with get_db() as conn:
        source_json = json.dumps(source_data) if source_data and not isinstance(source_data, str) else source_data
        target_json = json.dumps(target_data) if target_data and not isinstance(target_data, str) else target_data
        if USE_POSTGRES:
            query = '''INSERT INTO format_conversions
                       (source_format, target_format, source_data, target_data, conversion_status, error_message)
                       VALUES (%s, %s, %s, %s, %s, %s) RETURNING id'''
            params = (source_format, target_format, source_json, target_json, conversion_status, error_message)
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result['id']
        else:
            query = '''INSERT INTO format_conversions
                       (source_format, target_format, source_data, target_data, conversion_status, error_message)
                       VALUES (?, ?, ?, ?, ?, ?)'''
            params = (source_format, target_format, source_json, target_json, conversion_status, error_message)
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid

def get_format_conversion_by_id(conversion_id):
    """
    Get specific format conversion by ID
    
    Args:
        conversion_id: Format conversion ID
    
    Returns:
        dict: Format conversion data or None if not found
    """
    with get_db() as conn:
        ph = '%s' if USE_POSTGRES else '?'
        row = execute_query_one(conn, f'SELECT * FROM format_conversions WHERE id = {ph}', (conversion_id,))
        return dict(row) if row else None

def get_all_format_conversions(limit=None):
    """
    Get all format conversions with optional limit
    
    Args:
        limit: Maximum number of results (optional)
    
    Returns:
        list: List of format conversion dictionaries
    """
    with get_db() as conn:
        query = 'SELECT * FROM format_conversions ORDER BY created_at DESC'
        params = []
        
        if limit:
            ph = '%s' if USE_POSTGRES else '?'
            query += f' LIMIT {ph}'
            params.append(limit)
        
        rows = execute_query(conn, query, params)
        return [dict(row) for row in rows]

def get_conversions_by_formats(source_format=None, target_format=None, limit=None):
    """
    Get format conversions filtered by source and/or target format
    
    Args:
        source_format: Filter by source format (optional)
        target_format: Filter by target format (optional)
        limit: Maximum number of results (optional)
    
    Returns:
        list: List of format conversion dictionaries
    """
    with get_db() as conn:
        query = 'SELECT * FROM format_conversions'
        params = []
        conditions = []
        ph = '%s' if USE_POSTGRES else '?'
        
        if source_format:
            conditions.append(f'source_format = {ph}')
            params.append(source_format)
        
        if target_format:
            conditions.append(f'target_format = {ph}')
            params.append(target_format)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY created_at DESC'
        
        if limit:
            query += f' LIMIT {ph}'
            params.append(limit)
        
        rows = execute_query(conn, query, params)
        return [dict(row) for row in rows]

def delete_format_conversion(conversion_id):
    """
    Delete a format conversion record
    
    Args:
        conversion_id: Format conversion ID to delete
    
    Returns:
        bool: True if deletion was successful
    """
    with get_db() as conn:
        ph = '%s' if USE_POSTGRES else '?'
        execute_update(conn, f'DELETE FROM format_conversions WHERE id = {ph}', (conversion_id,))
        return True

# Agent Cards CRUD
def create_agent_card(entity_type, entity_id, card_data, card_version='1.0', published=False):
    """
    Create a new agent card
    
    Args:
        entity_type: Entity type ('template', 'configuration', 'custom_agent')
        entity_id: Entity ID
        card_data: Agent card data as dictionary
        card_version: Card version (default: '1.0')
        published: Whether the card is published (default: False)
    
    Returns:
        int: The ID of the created agent card
    """
    print(f"DB DEBUG: Creating card for entity_type={entity_type}, entity_id={entity_id}")
    with get_db() as conn:
        card_json = json.dumps(card_data) if isinstance(card_data, dict) else card_data
        if USE_POSTGRES:
            query = '''INSERT INTO agent_cards (entity_type, entity_id, card_data, card_version, published)
                       VALUES (%s, %s, %s, %s, %s) RETURNING id'''
            params = (entity_type, entity_id, card_json, card_version, convert_bool(published))
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            print(f"DB DEBUG: Created card with id={result['id']}")
            return result['id']
        else:
            query = '''INSERT INTO agent_cards (entity_type, entity_id, card_data, card_version, published)
                       VALUES (?, ?, ?, ?, ?)'''
            params = (entity_type, entity_id, card_json, card_version, published)
            cursor = conn.cursor()
            cursor.execute(query, params)
            print(f"DB DEBUG: Created card with id={cursor.lastrowid}")
            return cursor.lastrowid

def get_agent_card_by_id(card_id):
    """
    Get specific agent card by ID
    
    Args:
        card_id: Agent card ID
    
    Returns:
        dict: Agent card data or None if not found
    """
    with get_db() as conn:
        ph = '%s' if USE_POSTGRES else '?'
        row = execute_query_one(conn, f'SELECT * FROM agent_cards WHERE id = {ph}', (card_id,))
        if row:
            card_dict = dict(row)
            # Parse card_data from JSON string to dict
            if card_dict.get('card_data'):
                try:
                    card_dict['card_data'] = json.loads(card_dict['card_data'])
                except json.JSONDecodeError:
                    pass
            return card_dict
        return None

def get_agent_card_by_entity(entity_type, entity_id):
    """
    Get agent card by entity type and ID
    
    Args:
        entity_type: Entity type ('template', 'configuration', 'custom_agent')
        entity_id: Entity ID
    
    Returns:
        dict: Agent card data or None if not found
    """
    with get_db() as conn:
        ph = '%s' if USE_POSTGRES else '?'
        row = execute_query_one(conn, f'SELECT * FROM agent_cards WHERE entity_type = {ph} AND entity_id = {ph}', (entity_type, entity_id))
        if row:
            card_dict = dict(row)
            # Parse card_data from JSON string to dict
            if card_dict.get('card_data'):
                try:
                    card_dict['card_data'] = json.loads(card_dict['card_data'])
                except json.JSONDecodeError:
                    pass
            return card_dict
        return None

def get_all_agent_cards(entity_type=None, published=None):
    """
    Get all agent cards with optional filtering
    
    Args:
        entity_type: Filter by entity type (optional)
        published: Filter by published status (optional)
    
    Returns:
        list: List of agent card dictionaries
    """
    with get_db() as conn:
        query = 'SELECT * FROM agent_cards'
        params = []
        conditions = []
        ph = '%s' if USE_POSTGRES else '?'
        
        if entity_type:
            conditions.append(f'entity_type = {ph}')
            params.append(entity_type)
        
        if published is not None:
            conditions.append(f'published = {ph}')
            params.append(convert_bool(published) if USE_POSTGRES else (1 if published else 0))
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY updated_at DESC'
        
        rows = execute_query(conn, query, params)
        cards = []
        for row in rows:
            card_dict = dict(row)
            # Parse card_data from JSON string to dict
            if card_dict.get('card_data'):
                try:
                    card_dict['card_data'] = json.loads(card_dict['card_data'])
                except json.JSONDecodeError:
                    pass
            cards.append(card_dict)
        return cards

def update_agent_card(card_id, card_data=None, published=None):
    """
    Update existing agent card
    
    Args:
        card_id: Agent card ID to update
        card_data: New card data (optional)
        published: New published status (optional)
    
    Returns:
        int: The ID of the updated agent card
    """
    with get_db() as conn:
        update_fields = ['updated_at = CURRENT_TIMESTAMP']
        params = []
        ph = '%s' if USE_POSTGRES else '?'
        
        if card_data is not None:
            card_json = json.dumps(card_data) if isinstance(card_data, dict) else card_data
            update_fields.append(f'card_data = {ph}')
            params.append(card_json)
        
        if published is not None:
            update_fields.append(f'published = {ph}')
            params.append(convert_bool(published) if USE_POSTGRES else (1 if published else 0))
        
        params.append(card_id)
        query = f"UPDATE agent_cards SET {', '.join(update_fields)} WHERE id = {ph}"
        execute_update(conn, query, params)
        return card_id

def delete_agent_card(card_id):
    """
    Delete agent card
    
    Args:
        card_id: Agent card ID to delete
    
    Returns:
        bool: True if deletion was successful
    """
    with get_db() as conn:
        ph = '%s' if USE_POSTGRES else '?'
        execute_update(conn, f'DELETE FROM agent_cards WHERE id = {ph}', (card_id,))
        return True

def get_agent_cards_by_type(entity_type):
    """
    Get agent cards filtered by entity type
    
    Args:
        entity_type: Entity type ('template', 'configuration', 'custom_agent')
    
    Returns:
        list: List of agent card dictionaries
    """
    with get_db() as conn:
        ph = '%s' if USE_POSTGRES else '?'
        rows = execute_query(conn, f'SELECT * FROM agent_cards WHERE entity_type = {ph} ORDER BY updated_at DESC', (entity_type,))
        cards = []
        for row in rows:
            card_dict = dict(row)
            # Parse card_data from JSON string to dict
            if card_dict.get('card_data'):
                try:
                    card_dict['card_data'] = json.loads(card_dict['card_data'])
                except json.JSONDecodeError:
                    pass
            cards.append(card_dict)
        return cards

# Auto-generation hooks for agent cards
def _generate_and_store_agent_card(entity_type, entity_id):
    """
    Generate and store an agent card for an entity
    
    Args:
        entity_type: Entity type ('template', 'configuration', 'custom_agent')
        entity_id: Entity ID
    
    Returns:
        int: The ID of the created/updated agent card or None if failed
    """
    try:
        import generators
        
        # Get entity data
        if entity_type == 'template':
            entity_data = get_template_by_id(entity_id)
            if entity_data:
                card_data = generators.AgentCardGenerator.generate_from_template(entity_data)
        elif entity_type == 'configuration':
            entity_data = get_configuration_by_id(entity_id)
            if entity_data:
                card_data = generators.AgentCardGenerator.generate_from_configuration(entity_data)
        elif entity_type == 'custom_agent':
            entity_data = get_custom_agent_by_id(entity_id)
            if entity_data:
                card_data = generators.AgentCardGenerator.generate_from_custom_agent(entity_data)
        else:
            return None
        
        if not entity_data:
            return None
        
        # Check if card already exists
        existing_card = get_agent_card_by_entity(entity_type, entity_id)
        
        if existing_card:
            # Update existing card
            update_agent_card(existing_card['id'], card_data=card_data)
            return existing_card['id']
        else:
            # Create new card
            return create_agent_card(entity_type, entity_id, card_data)
    except Exception as e:
        # Log error but don't raise - agent card generation should not block entity creation
        print(f"Error generating agent card for {entity_type} {entity_id}: {e}")
        return None
