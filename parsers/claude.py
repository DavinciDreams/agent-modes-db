"""
Claude agent format parser.

This module provides the ClaudeParser class for parsing
Claude agent format definitions into AgentIR.
"""

from typing import Dict, Any, Tuple, List
from . import BaseParser


class ClaudeParser(BaseParser):
    """Parser for Claude agent format."""
    
    def parse(self, content: str) -> 'AgentIR':
        """
        Parse Claude agent format content.
        
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
            raise ValueError("Claude agent content must be an object/dictionary")
        
        # Validate the Claude format
        is_valid, errors = self.validate(data)
        if not is_valid:
            raise ValueError(f"Invalid Claude agent format: {', '.join(errors)}")
        
        # Convert to AgentIR
        ir = AgentIR()
        ir.name = data.get('name')
        ir.description = data.get('description')
        ir.version = data.get('version', '1.0.0')
        ir.capabilities = data.get('capabilities', [])
        ir.tools = data.get('tools', [])
        ir.system_prompt = data.get('system_prompt')
        ir.config_schema = data.get('config_schema')
        ir.metadata = data.get('metadata', {})
        
        # Handle config_json if present
        if 'config' in data:
            ir.config_json = data['config']
        
        # Extract additional fields as custom fields
        excluded_fields = {
            'name', 'description', 'version', 'capabilities', 'tools', 
            'system_prompt', 'config_schema', 'metadata', 'config'
        }
        for key, value in data.items():
            if key not in excluded_fields:
                ir.set_custom_field(key, value)
        
        return ir
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Claude agent format data.
        
        Args:
            data: The parsed data to validate
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        # Required fields
        required_fields = ['name', 'description']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: '{field}'")
            elif not data[field]:
                errors.append(f"Field '{field}' cannot be empty")
        
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
        
        if 'metadata' in data and data['metadata']:
            if not isinstance(data['metadata'], dict):
                errors.append("'metadata' must be a dictionary")
        
        if 'config_schema' in data and data['config_schema']:
            if not isinstance(data['config_schema'], dict):
                errors.append("'config_schema' must be a dictionary")
        
        if 'version' in data and data['version']:
            if not isinstance(data['version'], str):
                errors.append("'version' must be a string")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_format_name(cls) -> str:
        """Get the format name for this parser."""
        return "claude"
    
    @classmethod
    def get_format_description(cls) -> str:
        """Get the format description for this parser."""
        return "Anthropic Claude agent format with name, description, capabilities, tools, and system_prompt fields"