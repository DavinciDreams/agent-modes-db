"""
Custom agent format parser.

This module provides the CustomParser class for parsing
custom application-specific agent format definitions into AgentIR.
"""

from typing import Dict, Any, Tuple, List
from . import BaseParser


class CustomParser(BaseParser):
    """Parser for custom application-specific agent format."""
    
    def parse(self, content: str) -> 'AgentIR':
        """
        Parse custom agent format content.
        
        Args:
            content: The content to parse (string representation)
        
        Returns:
            AgentIR: Parsed agent data as intermediate representation
        
        Raises:
            ValueError: If parsing fails
        """
        from converters.ir import AgentIR  # Lazy import to avoid circular dependency
        
        # First parse content as JSON/YAML
        import json
        try:
            # Try JSON first
            data = json.loads(content)
        except json.JSONDecodeError:
            # Try YAML if JSON fails
            try:
                import yaml
                data = yaml.safe_load(content)
            except ImportError:
                raise ValueError("PyYAML is not installed. Install it with: pip install PyYAML")
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML: {str(e)}")
        
        if not isinstance(data, dict):
            raise ValueError("Custom agent content must be an object/dictionary")
        
        # Validate custom format
        is_valid, errors = self.validate(data)
        if not is_valid:
            raise ValueError(f"Invalid custom agent format: {', '.join(errors)}")
        
        # Convert to AgentIR
        ir = AgentIR()
        ir.name = data.get('name')
        ir.description = data.get('description')
        ir.version = data.get('version', '1.0.0')
        ir.category = data.get('category')
        ir.capabilities = data.get('capabilities', [])
        ir.tools = data.get('tools', [])
        ir.system_prompt = data.get('system_prompt')
        ir.config_schema = data.get('config_schema')
        ir.config_json = data.get('config')
        ir.metadata = data.get('metadata', {})
        ir.icon = data.get('icon')
        ir.author = data.get('author')
        ir.tags = data.get('tags', [])
        
        # Extract additional fields as custom fields
        excluded_fields = {
            'name', 'description', 'version', 'category', 'capabilities', 'tools',
            'system_prompt', 'config_schema', 'config', 'metadata', 'icon', 'author', 'tags'
        }
        for key, value in data.items():
            if key not in excluded_fields:
                ir.set_custom_field(key, value)
        
        return ir
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate custom agent format data.
        
        Args:
            data: The parsed data to validate
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        # Required fields
        required_fields = ['name', 'description', 'capabilities', 'tools', 'system_prompt']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: '{field}'")
            elif not data[field]:
                errors.append(f"Field '{field}' cannot be empty")
        
        # Validate field types
        if 'capabilities' in data and data['capabilities']:
            if not isinstance(data['capabilities'], list):
                errors.append("'capabilities' must be a list")
            else:
                for i, cap in enumerate(data['capabilities']):
                    if not isinstance(cap, str):
                        errors.append(f"capabilities[{i}] must be a string")
        
        if 'tools' in data and data['tools']:
            if not isinstance(data['tools'], list):
                errors.append("'tools' must be a list")
            else:
                for i, tool in enumerate(data['tools']):
                    if not isinstance(tool, str):
                        errors.append(f"tools[{i}] must be a string")
        
        if 'tags' in data and data['tags']:
            if not isinstance(data['tags'], list):
                errors.append("'tags' must be a list")
            else:
                for i, tag in enumerate(data['tags']):
                    if not isinstance(tag, str):
                        errors.append(f"tags[{i}] must be a string")
        
        if 'metadata' in data and data['metadata']:
            if not isinstance(data['metadata'], dict):
                errors.append("'metadata' must be a dictionary")
        
        if 'config_schema' in data and data['config_schema']:
            if not isinstance(data['config_schema'], dict):
                errors.append("'config_schema' must be a dictionary")
        
        if 'config' in data and data['config']:
            if not isinstance(data['config'], dict):
                errors.append("'config' must be a dictionary")
        
        if 'version' in data and data['version']:
            if not isinstance(data['version'], str):
                errors.append("'version' must be a string")
        
        if 'category' in data and data['category']:
            if not isinstance(data['category'], str):
                errors.append("'category' must be a string")
        
        if 'icon' in data and data['icon']:
            if not isinstance(data['icon'], str):
                errors.append("'icon' must be a string")
        
        if 'author' in data and data['author']:
            if not isinstance(data['author'], str):
                errors.append("'author' must be a string")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_format_name(cls) -> str:
        """Get format name for this parser."""
        return "custom"
    
    @classmethod
    def get_format_description(cls) -> str:
        """Get the format description for this parser."""
        return "Application-specific custom agent format with comprehensive field support and validation"