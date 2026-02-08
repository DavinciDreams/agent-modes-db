"""
Claude agent format serializer.

This module provides the ClaudeSerializer class for converting
AgentIR to Claude agent format.
"""

from typing import Dict, Any
from . import BaseSerializer
from converters.ir import AgentIR


class ClaudeSerializer(BaseSerializer):
    """Serializer for Claude agent format."""
    
    def serialize(self, ir: AgentIR, output_format: str = 'json') -> Dict[str, Any]:
        """
        Serialize AgentIR to Claude agent format.
        
        Args:
            ir: The AgentIR to serialize
            output_format: Output format ('json' or 'yaml')
        
        Returns:
            dict: Serialized Claude agent data
        
        Raises:
            ValueError: If serialization fails
        """
        # Validate the IR first
        is_valid, errors = ir.validate()
        if not is_valid:
            raise ValueError(f"Invalid AgentIR: {', '.join(errors)}")
        
        # Build Claude format data
        data = {
            'name': ir.name,
            'description': ir.description,
            'version': ir.version
        }
        
        # Add optional fields if they have values
        if ir.capabilities:
            data['capabilities'] = ir.capabilities
        
        if ir.tools:
            data['tools'] = ir.tools
        
        if ir.system_prompt:
            data['system_prompt'] = ir.system_prompt
        
        if ir.config_schema:
            data['config_schema'] = ir.config_schema
        
        if ir.config_json:
            data['config'] = ir.config_json
        
        # Add metadata if present
        if ir.metadata:
            data['metadata'] = ir.metadata
        
        # Add custom fields
        data.update(ir.custom_fields)
        
        return data
    
    @classmethod
    def get_format_name(cls) -> str:
        """Get the format name for this serializer."""
        return "claude"
    
    @classmethod
    def get_format_description(cls) -> str:
        """Get the format description for this serializer."""
        return "Anthropic Claude agent format with name, description, capabilities, tools, and system_prompt fields"