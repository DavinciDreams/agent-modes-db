"""
Custom agent format serializer.

This module provides the CustomSerializer class for converting
AgentIR to custom application-specific agent format.
"""

from typing import Dict, Any
from . import BaseSerializer
from converters.ir import AgentIR


class CustomSerializer(BaseSerializer):
    """Serializer for custom application-specific agent format."""
    
    def serialize(self, ir: AgentIR, output_format: str = 'json') -> Dict[str, Any]:
        """
        Serialize AgentIR to custom agent format.
        
        Args:
            ir: The AgentIR to serialize
            output_format: Output format ('json' or 'yaml')
        
        Returns:
            dict: Serialized custom agent data
        
        Raises:
            ValueError: If serialization fails
        """
        # Validate the IR first
        is_valid, errors = ir.validate()
        if not is_valid:
            raise ValueError(f"Invalid AgentIR: {', '.join(errors)}")
        
        # Build custom format data
        data = {
            'name': ir.name,
            'description': ir.description,
            'version': ir.version
        }
        
        # Add required fields for custom format
        if ir.capabilities:
            data['capabilities'] = ir.capabilities
        else:
            # Custom format requires capabilities, add empty list if not present
            data['capabilities'] = []
        
        if ir.tools:
            data['tools'] = ir.tools
        else:
            # Custom format requires tools, add empty list if not present
            data['tools'] = []
        
        if ir.system_prompt:
            data['system_prompt'] = ir.system_prompt
        else:
            # Custom format requires system_prompt, add default if not present
            data['system_prompt'] = f"You are {ir.name}, an AI assistant. {ir.description}"
        
        # Add optional fields
        if ir.category:
            data['category'] = ir.category
        
        if ir.config_schema:
            data['config_schema'] = ir.config_schema
        
        if ir.config_json:
            data['config'] = ir.config_json
        
        if ir.author:
            data['author'] = ir.author
        
        if ir.tags:
            data['tags'] = ir.tags
        
        if ir.icon:
            data['icon'] = ir.icon
        
        # Add metadata if present
        if ir.metadata:
            data['metadata'] = ir.metadata
        
        # Add custom fields
        data.update(ir.custom_fields)
        
        return data
    
    @classmethod
    def get_format_name(cls) -> str:
        """Get the format name for this serializer."""
        return "custom"
    
    @classmethod
    def get_format_description(cls) -> str:
        """Get the format description for this serializer."""
        return "Application-specific custom agent format with comprehensive field support and validation"