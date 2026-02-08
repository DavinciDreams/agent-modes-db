"""
Intermediate Representation (IR) for agent definitions.

This module defines the AgentIR class which serves as a unified
data model for agent definitions across different formats.
"""

import json
from typing import Dict, Any, List, Optional, Union


class AgentIR:
    """
    Intermediate Representation for agent definitions.
    
    This class provides a unified data model that can represent
    agent definitions from Claude, Roo, and custom formats.
    """
    
    def __init__(self):
        """Initialize a new AgentIR instance."""
        self.id: Optional[str] = None
        self.name: Optional[str] = None
        self.description: Optional[str] = None
        self.version: str = "1.0.0"
        self.category: Optional[str] = None
        self.capabilities: List[str] = []
        self.tools: List[str] = []
        self.system_prompt: Optional[str] = None
        self.config_json: Optional[Dict[str, Any]] = None
        self.config_schema: Optional[Dict[str, Any]] = None
        self.metadata: Dict[str, Any] = {}
        self.icon: Optional[str] = None
        self.author: Optional[str] = None
        self.tags: List[str] = []
        self.custom_fields: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert AgentIR to dictionary representation.
        
        Returns:
            dict: Dictionary representation of the agent
        """
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'category': self.category,
            'capabilities': self.capabilities,
            'tools': self.tools,
            'system_prompt': self.system_prompt,
            'config_json': self.config_json,
            'config_schema': self.config_schema,
            'metadata': self.metadata,
            'icon': self.icon,
            'author': self.author,
            'tags': self.tags,
            'custom_fields': self.custom_fields
        }
        
        # Remove None values to keep the dict clean
        return {k: v for k, v in result.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentIR':
        """
        Create AgentIR from dictionary representation.
        
        Args:
            data: Dictionary containing agent data
            
        Returns:
            AgentIR: New AgentIR instance
        """
        ir = cls()
        
        # Set basic fields
        ir.id = data.get('id')
        ir.name = data.get('name')
        ir.description = data.get('description')
        ir.version = data.get('version', '1.0.0')
        ir.category = data.get('category')
        ir.system_prompt = data.get('system_prompt')
        ir.icon = data.get('icon')
        ir.author = data.get('author')
        
        # Set list fields
        ir.capabilities = data.get('capabilities', [])
        ir.tools = data.get('tools', [])
        ir.tags = data.get('tags', [])
        
        # Set dict fields
        ir.config_json = data.get('config_json')
        ir.config_schema = data.get('config_schema')
        ir.metadata = data.get('metadata', {})
        ir.custom_fields = data.get('custom_fields', {})
        
        return ir
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate the AgentIR data.
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        if not self.name:
            errors.append("Missing required field: 'name'")
        
        if not self.description:
            errors.append("Missing required field: 'description'")
        
        # Check that at least one of the following is present
        if not self.system_prompt and not self.capabilities and not self.tools:
            errors.append("Agent must have at least one of: system_prompt, capabilities, tools")
        
        # Validate data types
        if self.capabilities and not isinstance(self.capabilities, list):
            errors.append("'capabilities' must be a list")
        
        if self.tools and not isinstance(self.tools, list):
            errors.append("'tools' must be a list")
        
        if self.tags and not isinstance(self.tags, list):
            errors.append("'tags' must be a list")
        
        if self.metadata and not isinstance(self.metadata, dict):
            errors.append("'metadata' must be a dictionary")
        
        if self.custom_fields and not isinstance(self.custom_fields, dict):
            errors.append("'custom_fields' must be a dictionary")
        
        return len(errors) == 0, errors
    
    def merge_capabilities(self, additional_capabilities: List[str]) -> None:
        """
        Merge additional capabilities, avoiding duplicates.
        
        Args:
            additional_capabilities: List of capabilities to add
        """
        for cap in additional_capabilities:
            if cap not in self.capabilities:
                self.capabilities.append(cap)
    
    def merge_tools(self, additional_tools: List[str]) -> None:
        """
        Merge additional tools, avoiding duplicates.
        
        Args:
            additional_tools: List of tools to add
        """
        for tool in additional_tools:
            if tool not in self.tools:
                self.tools.append(tool)
    
    def add_tag(self, tag: str) -> None:
        """
        Add a tag if it doesn't already exist.
        
        Args:
            tag: Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata value.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)
    
    def set_custom_field(self, key: str, value: Any) -> None:
        """
        Set custom field value.
        
        Args:
            key: Custom field key
            value: Custom field value
        """
        self.custom_fields[key] = value
    
    def get_custom_field(self, key: str, default: Any = None) -> Any:
        """
        Get custom field value.
        
        Args:
            key: Custom field key
            default: Default value if key not found
            
        Returns:
            Custom field value or default
        """
        return self.custom_fields.get(key, default)
    
    def __str__(self) -> str:
        """String representation of AgentIR."""
        return f"AgentIR(name='{self.name}', category='{self.category}', capabilities={len(self.capabilities)})"
    
    def __repr__(self) -> str:
        """Detailed string representation of AgentIR."""
        return f"AgentIR(id={self.id}, name='{self.name}', description='{self.description[:50] if self.description else None}...')"