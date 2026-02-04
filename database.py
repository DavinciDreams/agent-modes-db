import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

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
    """Initialize database with schema"""
    with open('schema.sql', 'r') as f:
        schema = f.read()

    with get_db() as conn:
        conn.executescript(schema)

    # Add seed data
    seed_builtin_templates()

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

def create_template(name, description, category, is_builtin=False):
    """Create new agent template"""
    with get_db() as conn:
        cursor = conn.execute(
            '''INSERT INTO agent_templates (name, description, category, is_builtin)
               VALUES (?, ?, ?, ?)''',
            (name, description, category, is_builtin)
        )
        return cursor.lastrowid

def update_template(template_id, name, description, category):
    """Update existing template"""
    with get_db() as conn:
        conn.execute(
            '''UPDATE agent_templates
               SET name = ?, description = ?, category = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?''',
            (name, description, category, template_id)
        )
        return template_id

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
        return cursor.lastrowid

def update_configuration(config_id, name, template_id, config_json):
    """Update existing configuration"""
    with get_db() as conn:
        conn.execute(
            '''UPDATE agent_configurations
               SET name = ?, template_id = ?, config_json = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?''',
            (name, template_id, json.dumps(config_json) if isinstance(config_json, dict) else config_json, config_id)
        )
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

def create_custom_agent(name, description, capabilities, tools, system_prompt, config_schema=None):
    """Create new custom agent"""
    with get_db() as conn:
        cursor = conn.execute(
            '''INSERT INTO custom_agents (name, description, capabilities, tools, system_prompt, config_schema)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (
                name,
                description,
                json.dumps(capabilities) if isinstance(capabilities, list) else capabilities,
                json.dumps(tools) if isinstance(tools, list) else tools,
                system_prompt,
                json.dumps(config_schema) if config_schema and isinstance(config_schema, dict) else config_schema
            )
        )
        return cursor.lastrowid

def update_custom_agent(agent_id, name, description, capabilities, tools, system_prompt, config_schema=None):
    """Update existing custom agent"""
    with get_db() as conn:
        conn.execute(
            '''UPDATE custom_agents
               SET name = ?, description = ?, capabilities = ?, tools = ?,
                   system_prompt = ?, config_schema = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?''',
            (
                name,
                description,
                json.dumps(capabilities) if isinstance(capabilities, list) else capabilities,
                json.dumps(tools) if isinstance(tools, list) else tools,
                system_prompt,
                json.dumps(config_schema) if config_schema and isinstance(config_schema, dict) else config_schema,
                agent_id
            )
        )
        return agent_id

def delete_custom_agent(agent_id):
    """Delete custom agent"""
    with get_db() as conn:
        conn.execute('DELETE FROM custom_agents WHERE id = ?', (agent_id,))
        return True
