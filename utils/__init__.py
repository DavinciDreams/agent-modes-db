"""
Utility functions for file handling and validation.

This module provides utility functions for reading files,
validating data formats, and extracting metadata from parsed data.
"""

import json
import os
from typing import Dict, Any, Tuple, Optional


def read_file_content(file_path: str, encoding: str = 'utf-8') -> str:
    """
    Read file content with encoding detection.
    
    Args:
        file_path: Path to the file to read
        encoding: Character encoding to use (default: utf-8)
    
    Returns:
        str: File content
    
    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If encoding fails
        IOError: If reading fails
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # Try alternative encodings if utf-8 fails
        for alt_encoding in ['utf-8-sig', 'latin-1', 'cp1252']:
            try:
                with open(file_path, 'r', encoding=alt_encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError(f"Could not decode file {file_path} with any common encoding")


def validate_json(content: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Validate JSON structure.
    
    Args:
        content: JSON string to validate
    
    Returns:
        tuple: (is_valid, parsed_data, error_message)
    """
    try:
        data = json.loads(content)
        if not isinstance(data, dict):
            return False, None, "JSON must be an object/dictionary"
        return True, data, None
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON: {str(e)}"


def validate_yaml(content: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Validate YAML structure.
    
    Args:
        content: YAML string to validate
    
    Returns:
        tuple: (is_valid, parsed_data, error_message)
    """
    try:
        import yaml
        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            return False, None, "YAML must be a dictionary/object"
        return True, data, None
    except ImportError:
        return False, None, "PyYAML is not installed. Install it with: pip install PyYAML"
    except yaml.YAMLError as e:
        return False, None, f"Invalid YAML: {str(e)}"


def extract_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract common metadata from parsed agent data.
    
    Args:
        data: Parsed agent data
    
    Returns:
        dict: Extracted metadata
    """
    metadata = {}
    
    # Common metadata fields
    metadata_fields = [
        'name',
        'description',
        'version',
        'author',
        'category',
        'tags',
        'created_at',
        'updated_at',
        'license',
        'source_url'
    ]
    
    for field in metadata_fields:
        if field in data:
            metadata[field] = data[field]
    
    # Extract agent-specific fields
    agent_fields = {
        'capabilities': [],
        'tools': [],
        'system_prompt': None,
        'config_schema': None
    }
    
    for field, default in agent_fields.items():
        if field in data:
            metadata[field] = data[field]
        else:
            metadata[field] = default
    
    return metadata


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other issues.
    
    Args:
        filename: Original filename
    
    Returns:
        str: Sanitized filename
    """
    import re
    
    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')
    
    # Remove null bytes
    filename = filename.replace('\x00', '')
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit filename length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255 - len(ext)] + ext
    
    return filename


def get_file_size_human_readable(size_bytes: int) -> str:
    """
    Convert file size in bytes to human-readable format.
    
    Args:
        size_bytes: File size in bytes
    
    Returns:
        str: Human-readable file size (e.g., "1.5 KB", "2.3 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def is_valid_file_format(filename: str, allowed_formats: list = None) -> bool:
    """
    Check if file has a valid format.
    
    Args:
        filename: Filename to check
        allowed_formats: List of allowed extensions (e.g., ['.json', '.yaml', '.md'])
    
    Returns:
        bool: True if format is valid
    """
    if allowed_formats is None:
        allowed_formats = ['.json', '.yaml', '.yml', '.md', '.markdown']
    
    _, ext = os.path.splitext(filename.lower())
    return ext in allowed_formats


def normalize_agent_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize agent data to ensure consistent structure.
    
    Args:
        data: Raw agent data
    
    Returns:
        dict: Normalized agent data
    """
    normalized = {}
    
    # Ensure required fields exist
    normalized['name'] = data.get('name', 'Unnamed Agent')
    normalized['description'] = data.get('description', '')
    
    # Ensure lists for array fields
    for field in ['capabilities', 'tools', 'tags']:
        value = data.get(field)
        if isinstance(value, str):
            # Try to parse JSON string
            try:
                normalized[field] = json.loads(value)
            except:
                # Split by comma if JSON parsing fails
                normalized[field] = [item.strip() for item in value.split(',')]
        elif isinstance(value, list):
            normalized[field] = value
        else:
            normalized[field] = []
    
    # Handle optional fields
    optional_fields = ['system_prompt', 'config_schema', 'category', 'version']
    for field in optional_fields:
        if field in data:
            normalized[field] = data[field]
    
    # Preserve any additional fields
    for key, value in data.items():
        if key not in normalized:
            normalized[key] = value
    
    return normalized


# Export main functions
__all__ = [
    'read_file_content',
    'validate_json',
    'validate_yaml',
    'extract_metadata',
    'sanitize_filename',
    'get_file_size_human_readable',
    'is_valid_file_format',
    'normalize_agent_data'
]
