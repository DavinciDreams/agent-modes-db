#!/usr/bin/env python3
"""Retroactively create agents from existing file uploads"""

import database as db
import validators
import json
import re

def create_agent_from_upload(upload_id):
    """Create an agent from an existing upload"""
    upload = db.get_file_upload_by_id(upload_id)
    if not upload:
        return None

    # Check if agent already exists for this upload
    with db.get_db() as conn:
        ph = '%s' if db.USE_POSTGRES else '?'
        query = f"SELECT id FROM agents WHERE source_file_id = {ph}"
        existing = db.execute_query_one(conn, query, (upload_id,))

    if existing:
        agent_id = existing['id'] if db.USE_POSTGRES else existing[0]
        print(f"  Agent already exists for upload {upload_id}: agent ID {agent_id}")
        return None

    # Parse stored data
    try:
        normalized_data = json.loads(upload['parse_result']) if upload['parse_result'] else {}
    except:
        print(f"  Failed to parse upload {upload_id}")
        return None

    # Generate slug
    base_name = upload['original_filename'].rsplit('.', 1)[0]
    slug = re.sub(r'[^a-z0-9-]', '-', base_name.lower())
    slug = re.sub(r'-+', '-', slug).strip('-')

    # Ensure unique slug
    counter = 1
    original_slug = slug
    while db.get_agent_by_slug(slug):
        slug = f"{original_slug}-{counter}"
        counter += 1

    # Build config
    agent_config = {
        'slug': slug,
        'name': normalized_data.get('name', base_name.replace('-', ' ').title()),
        'description': normalized_data.get('description', ''),
        'instructions': normalized_data.get('instructions') or normalized_data.get('system_prompt', ''),
        'tools': normalized_data.get('tools', []),
        'skills': normalized_data.get('skills', []),
        'default_model': normalized_data.get('default_model', 'sonnet'),
        'max_turns': normalized_data.get('max_turns', 50),
        'source_format': upload.get('file_format', 'custom'),
        'source_file_id': upload_id
    }

    # Only add optional fields if they exist
    if normalized_data.get('allowed_edit_patterns'):
        agent_config['allowed_edit_patterns'] = normalized_data['allowed_edit_patterns']

    agent_config['metadata'] = {
        'author': normalized_data.get('author', 'Unknown'),
        'version': normalized_data.get('version', '1.0.0'),
        'source': 'upload',
        'original_filename': upload['original_filename']
    }

    # Validate
    is_valid, errors = validators.validate_agent(agent_config)
    if not is_valid:
        print(f"  Validation failed: {errors[0]}")
        return None

    # Create
    try:
        agent_id = db.create_agent(**agent_config)
        print(f"  ✓ Created '{slug}' (ID: {agent_id})")
        return agent_id
    except Exception as e:
        print(f"  Failed: {e}")
        return None

if __name__ == "__main__":
    print("Creating agents from existing uploads...\n")

    uploads = db.get_all_file_uploads()
    completed = [u for u in uploads if u['upload_status'] == 'completed']

    print(f"Found {len(completed)} completed uploads\n")

    created = 0
    for upload in completed:
        print(f"Upload {upload['id']}: {upload['original_filename']}")
        if create_agent_from_upload(upload['id']):
            created += 1

    print(f"\n{'='*60}")
    print(f"Created {created} agents from {len(completed)} uploads")
