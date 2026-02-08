"""
Roo agent format parser.

This module provides the RooParser class for parsing
Roo agent format definitions into AgentIR.
"""

from typing import Dict, Any, Tuple, List
from . import BaseParser


class RooParser(BaseParser):
    """Parser for Roo agent format."""
    
    def parse(self, content: str) -> 'AgentIR':
        """
        Parse Roo agent format content.
        
        Args:
            content: The content to parse (string representation)
        
        Returns:
            AgentIR: Parsed agent data as intermediate representation
        
        Raises:
            ValueError: If parsing fails
        """
        from converters.ir import AgentIR  # Lazy import to avoid circular dependency
        
        # First parse the content as JSON/YAML
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
            raise ValueError("Roo agent content must be an object/dictionary")
        
        # Validate the Roo format
        is_valid, errors = self.validate(data)
        if not is_valid:
            raise ValueError(f"Invalid Roo agent format: {', '.join(errors)}")
        
        # Convert to AgentIR
        ir = AgentIR()
        
        # Roo format uses 'mode' as the identifier, but we want 'name'
        # If both are present, use 'name', otherwise derive from 'mode'
        if 'name' in data:
            ir.name = data['name']
        elif 'mode' in data:
            # Convert mode to a readable name
            mode = data['mode']
            ir.name = mode.replace('-', ' ').title()
        
        ir.description = data.get('description')
        ir.category = data.get('category')
        ir.capabilities = data.get('capabilities', [])
        ir.tools = data.get('tools', [])
        ir.system_prompt = data.get('system_prompt')
        ir.icon = data.get('icon')
        ir.tags = data.get('tags', [])
        
        # Handle version if present
        if 'version' in data:
            ir.version = data['version']
        
        # Handle metadata if present
        if 'metadata' in data:
            ir.metadata = data['metadata']
        
        # Handle config if present
        if 'config' in data:
            ir.config_json = data['config']
        
        # Extract additional fields as custom fields
        excluded_fields = {
            'mode', 'name', 'description', 'category', 'capabilities', 'tools',
            'system_prompt', 'icon', 'tags', 'version', 'metadata', 'config'
        }
        for key, value in data.items():
            if key not in excluded_fields:
                ir.set_custom_field(key, value)
        
        # Store the original mode as metadata
        if 'mode' in data:
            ir.set_metadata('original_mode', data['mode'])
        
        return ir
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Roo agent format data.
        
        Args:
            data: The parsed data to validate
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        # Roo format requires either 'mode' or 'name'
        if 'mode' not in data and 'name' not in data:
            errors.append("Must have either 'mode' or 'name' field")
        
        if 'mode' in data and not data['mode']:
            errors.append("Field 'mode' cannot be empty")
        
        if 'name' in data and not data['name']:
            errors.append("Field 'name' cannot be empty")
        
        # Description is required
        if 'description' not in data:
            errors.append("Missing required field: 'description'")
        elif not data['description']:
            errors.append("Field 'description' cannot be empty")
        
        # Check for at least one agent-specific field
        agent_fields = ['system_prompt', 'capabilities', 'tools']
        if not any(field in data and data[field] for field in agent_fields):
            errors.append(f"Must have at least one of: {', '.join(agent_fields)}")
        
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
        
        if 'version' in data and data['version']:
            if not isinstance(data['version'], str):
                errors.append("'version' must be a string")
        
        if 'category' in data and data['category']:
            if not isinstance(data['category'], str):
                errors.append("'category' must be a string")
        
        if 'icon' in data and data['icon']:
            if not isinstance(data['icon'], str):
                errors.append("'icon' must be a string")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_format_name(cls) -> str:
        """Get the format name for this parser."""
        return "roo"
    
    @classmethod
    def get_format_description(cls) -> str:
        """Get the format description for this parser."""
        return "Roo Code agent format with mode, name, description, category, capabilities, tools, icon, and tags fields"