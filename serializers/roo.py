"""
Roo agent format serializer.

This module provides the RooSerializer class for converting
AgentIR to Roo agent format.
"""

from typing import Dict, Any
from . import BaseSerializer
from converters.ir import AgentIR


class RooSerializer(BaseSerializer):
    """Serializer for Roo agent format."""
    
    def serialize(self, ir: AgentIR, output_format: str = 'json') -> Dict[str, Any]:
        """
        Serialize AgentIR to Roo agent format.
        
        Args:
            ir: The AgentIR to serialize
            output_format: Output format ('json' or 'yaml')
        
        Returns:
            dict: Serialized Roo agent data
        
        Raises:
            ValueError: If serialization fails
        """
        # Validate the IR first
        is_valid, errors = ir.validate()
        if not is_valid:
            raise ValueError(f"Invalid AgentIR: {', '.join(errors)}")
        
        # Build Roo format data
        data = {
            'mode': ir.name.lower().replace(' ', '-'),
            'name': ir.name,
            'description': ir.description,
            'version': ir.version
        }
        
        # Add optional fields with defaults if needed
        data['category'] = ir.category or 'general'
        data['icon'] = ir.icon or 'fa-robot'
        data['tags'] = ir.tags if ir.tags else []
        
        # Add capabilities and tools if present
        if ir.capabilities:
            data['capabilities'] = ir.capabilities
        
        if ir.tools:
            data['tools'] = ir.tools
        
        if ir.system_prompt:
            data['system_prompt'] = ir.system_prompt
        
        # Add config if present
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
        return "roo"
    
    @classmethod
    def get_format_description(cls) -> str:
        """Get the format description for this serializer."""
        return "Roo Code agent format with mode, name, description, category, capabilities, tools, icon, and tags fields"