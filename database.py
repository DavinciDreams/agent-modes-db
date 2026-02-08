import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager

# Determine database file path based on environment
# On Vercel serverless functions, only /tmp is writable
if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
    DB_FILE = '/tmp/modes.db'
else:
    DB_FILE = 'agents.db'

@contextmanager
def get_db():
    """Context manager for database connections"""
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

def init_db():
    """Initialize database with schema and apply all migrations"""
    with open('schema.sql', 'r') as f:
        schema = f.read()

    with get_db() as conn:
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

def apply_migration(migration_file):
    """
    Apply a database migration script
    
    Args:
        migration_file: Path to the migration SQL file
    
    Returns:
        bool: True if migration was applied successfully
    """
    migration_path = os.path.join('migrations', migration_file)
    if not os.path.exists(migration_path):
        raise FileNotFoundError(f"Migration file not found: {migration_path}")
    
    with open(migration_path, 'r') as f:
        migration_sql = f.read()
    
    with get_db() as conn:
        try:
            conn.executescript(migration_sql)
            return True
        except Exception as e:
            # If error is about duplicate column, it's already migrated (idempotent)
            if 'duplicate column' in str(e).lower():
                return True
            raise e

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
            existing = conn.execute(
                'SELECT id FROM agent_templates WHERE name = ? AND is_builtin = 1',
                (template['name'],)
            ).fetchone()

            if not existing:
                conn.execute(
                    '''INSERT INTO agent_templates (name, description, category, is_builtin)
                       VALUES (?, ?, ?, ?)''',
                    (template['name'], template['description'], template['category'], template['is_builtin'])
                )

# Agent Templates CRUD
def get_all_templates():
    """Get all agent templates"""
    with get_db() as conn:
        rows = conn.execute(
            'SELECT * FROM agent_templates ORDER BY is_builtin DESC, name ASC'
        ).fetchall()
        return [dict(row) for row in rows]

def get_template_by_id(template_id):
    """Get specific template by ID"""
    with get_db() as conn:
        row = conn.execute(
            'SELECT * FROM agent_templates WHERE id = ?',
            (template_id,)
        ).fetchone()
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
        cursor = conn.execute(
            '''INSERT INTO agent_templates (name, description, category, is_builtin, source_format, source_file_id, is_imported)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (name, description, category, is_builtin, source_format, source_file_id, is_imported)
        )
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
        update_fields = ['name = ?', 'description = ?', 'category = ?', 'updated_at = CURRENT_TIMESTAMP']
        params = [name, description, category]
        
        if source_format is not None:
            update_fields.append('source_format = ?')
            params.append(source_format)
        
        if source_file_id is not None:
            update_fields.append('source_file_id = ?')
            params.append(source_file_id)
        
        if is_imported is not None:
            update_fields.append('is_imported = ?')
            params.append(is_imported)
        
        params.append(template_id)
        
        query = f"UPDATE agent_templates SET {', '.join(update_fields)} WHERE id = ?"
        conn.execute(query, params)
    
    # Auto-regenerate agent card for the updated template
    _generate_and_store_agent_card('template', template_id)
    # _generate_and_store_agent_card("template", template_id)    return template_id

def delete_template(template_id):
    """Delete template (only if not builtin)"""
    with get_db() as conn:
        # Check if builtin
        row = conn.execute(
            'SELECT is_builtin FROM agent_templates WHERE id = ?',
            (template_id,)
        ).fetchone()

        if row and row['is_builtin']:
            raise ValueError("Cannot delete builtin templates")

        conn.execute('DELETE FROM agent_templates WHERE id = ?', (template_id,))
        return True

# Agent Configurations CRUD
def get_all_configurations():
    """Get all agent configurations with template info"""
    with get_db() as conn:
        rows = conn.execute(
            '''SELECT c.*, t.name as template_name
               FROM agent_configurations c
               LEFT JOIN agent_templates t ON c.template_id = t.id
               ORDER BY c.updated_at DESC'''
        ).fetchall()
        return [dict(row) for row in rows]

def get_configuration_by_id(config_id):
    """Get specific configuration by ID"""
    with get_db() as conn:
        row = conn.execute(
            '''SELECT c.*, t.name as template_name
               FROM agent_configurations c
               LEFT JOIN agent_templates t ON c.template_id = t.id
               WHERE c.id = ?''',
            (config_id,)
        ).fetchone()
        return dict(row) if row else None

def create_configuration(name, template_id, config_json):
    """Create new agent configuration"""
    with get_db() as conn:
        cursor = conn.execute(
            '''INSERT INTO agent_configurations (name, template_id, config_json)
               VALUES (?, ?, ?)''',
            (name, template_id, json.dumps(config_json) if isinstance(config_json, dict) else config_json)
        )
        config_id = cursor.lastrowid
    
    # Auto-generate agent card for the new configuration
    _generate_and_store_agent_card('configuration', config_id)
    
    return config_id

def update_configuration(config_id, name, template_id, config_json):
    """Update existing configuration"""
    with get_db() as conn:
        conn.execute(
            '''UPDATE agent_configurations
               SET name = ?, template_id = ?, config_json = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?''',
            (name, template_id, json.dumps(config_json) if isinstance(config_json, dict) else config_json, config_id)
        )
    
    # Auto-regenerate agent card for the updated configuration
    _generate_and_store_agent_card('configuration', config_id)
    
    return config_id

def delete_configuration(config_id):
    """Delete configuration"""
    with get_db() as conn:
        conn.execute('DELETE FROM agent_configurations WHERE id = ?', (config_id,))
        return True

# Custom Agents CRUD
def get_all_custom_agents():
    """Get all custom agents"""
    with get_db() as conn:
        rows = conn.execute(
            'SELECT * FROM custom_agents ORDER BY updated_at DESC'
        ).fetchall()
        return [dict(row) for row in rows]

def get_custom_agent_by_id(agent_id):
    """Get specific custom agent by ID"""
    with get_db() as conn:
        row = conn.execute(
            'SELECT * FROM custom_agents WHERE id = ?',
            (agent_id,)
        ).fetchone()
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
        cursor = conn.execute(
            '''INSERT INTO custom_agents (name, description, capabilities, tools, system_prompt, config_schema, source_format, source_file_id, is_imported)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
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
        )
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
        update_fields = ['name = ?', 'description = ?', 'capabilities = ?', 'tools = ?',
                        'system_prompt = ?', 'updated_at = CURRENT_TIMESTAMP']
        params = [
            name,
            description,
            json.dumps(capabilities) if isinstance(capabilities, list) else capabilities,
            json.dumps(tools) if isinstance(tools, list) else tools,
            system_prompt
        ]
        
        if config_schema is not None:
            update_fields.append('config_schema = ?')
            params.append(json.dumps(config_schema) if isinstance(config_schema, dict) else config_schema)
        
        if source_format is not None:
            update_fields.append('source_format = ?')
            params.append(source_format)
        
        if source_file_id is not None:
            update_fields.append('source_file_id = ?')
            params.append(source_file_id)
        
        if is_imported is not None:
            update_fields.append('is_imported = ?')
            params.append(is_imported)
        
        params.append(agent_id)
        
        query = f"UPDATE custom_agents SET {', '.join(update_fields)} WHERE id = ?"
        conn.execute(query, params)
    
    # Auto-regenerate agent card for the updated custom agent
    _generate_and_store_agent_card('custom_agent', agent_id)
    
    return agent_id

def delete_custom_agent(agent_id):
    """Delete custom agent"""
    with get_db() as conn:
        conn.execute('DELETE FROM custom_agents WHERE id = ?', (agent_id,))
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
        cursor = conn.execute(
            '''INSERT INTO file_uploads (filename, original_filename, file_format, file_size, upload_status, parse_result, error_message)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (filename, original_filename, file_format, file_size, upload_status, parse_result_json, error_message)
        )
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
        row = conn.execute(
            'SELECT * FROM file_uploads WHERE id = ?',
            (upload_id,)
        ).fetchone()
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
            if status:
                conditions.append('upload_status = ?')
                params.append(status)
            if file_format:
                conditions.append('file_format = ?')
                params.append(file_format)
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY uploaded_at DESC'
        
        rows = conn.execute(query, params).fetchall()
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
        
        if upload_status is not None:
            update_fields.append('upload_status = ?')
            params.append(upload_status)
            if upload_status in ['completed', 'failed']:
                update_fields.append('processed_at = CURRENT_TIMESTAMP')
        
        if parse_result is not None:
            parse_result_json = json.dumps(parse_result) if parse_result and not isinstance(parse_result, str) else parse_result
            update_fields.append('parse_result = ?')
            params.append(parse_result_json)
        
        if error_message is not None:
            update_fields.append('error_message = ?')
            params.append(error_message)
        
        if not update_fields:
            return True
        
        params.append(upload_id)
        query = f"UPDATE file_uploads SET {', '.join(update_fields)} WHERE id = ?"
        conn.execute(query, params)
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
        conn.execute('DELETE FROM file_uploads WHERE id = ?', (upload_id,))
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
        cursor = conn.execute(
            '''INSERT INTO format_conversions
               (source_format, target_format, source_data, target_data, conversion_status, error_message)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (source_format, target_format, source_json, target_json, conversion_status, error_message)
        )
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
        row = conn.execute(
            'SELECT * FROM format_conversions WHERE id = ?',
            (conversion_id,)
        ).fetchone()
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
            query += ' LIMIT ?'
            params.append(limit)
        
        rows = conn.execute(query, params).fetchall()
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
        
        if source_format:
            conditions.append('source_format = ?')
            params.append(source_format)
        
        if target_format:
            conditions.append('target_format = ?')
            params.append(target_format)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY created_at DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        rows = conn.execute(query, params).fetchall()
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
        conn.execute('DELETE FROM format_conversions WHERE id = ?', (conversion_id,))
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
        cursor = conn.execute(
            '''INSERT INTO agent_cards (entity_type, entity_id, card_data, card_version, published)
               VALUES (?, ?, ?, ?, ?)''',
            (entity_type, entity_id, card_json, card_version, published)
        )
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
        row = conn.execute(
            'SELECT * FROM agent_cards WHERE id = ?',
            (card_id,)
        ).fetchone()
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
        row = conn.execute(
            'SELECT * FROM agent_cards WHERE entity_type = ? AND entity_id = ?',
            (entity_type, entity_id)
        ).fetchone()
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
        
        if entity_type:
            conditions.append('entity_type = ?')
            params.append(entity_type)
        
        if published is not None:
            conditions.append('published = ?')
            params.append(1 if published else 0)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY updated_at DESC'
        
        rows = conn.execute(query, params).fetchall()
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
        
        if card_data is not None:
            card_json = json.dumps(card_data) if isinstance(card_data, dict) else card_data
            update_fields.append('card_data = ?')
            params.append(card_json)
        
        if published is not None:
            update_fields.append('published = ?')
            params.append(1 if published else 0)
        
        params.append(card_id)
        query = f"UPDATE agent_cards SET {', '.join(update_fields)} WHERE id = ?"
        conn.execute(query, params)
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
        conn.execute('DELETE FROM agent_cards WHERE id = ?', (card_id,))
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
        rows = conn.execute(
            'SELECT * FROM agent_cards WHERE entity_type = ? ORDER BY updated_at DESC',
            (entity_type,)
        ).fetchall()
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
