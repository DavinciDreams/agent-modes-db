"""
Serializers module for agent format transformations.

This module provides base serializer classes and format-specific
serializers for converting AgentIR to different agent formats.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from converters.ir import AgentIR


class BaseSerializer(ABC):
    """
    Abstract base class for agent format serializers.
    
    All format-specific serializers should inherit from this class
    and implement the serialize() method.
    """
    
    @abstractmethod
    def serialize(self, ir: AgentIR, output_format: str = 'json') -> Dict[str, Any]:
        """
        Serialize AgentIR to target format.
        
        Args:
            ir: The AgentIR to serialize
            output_format: Output format ('json' or 'yaml')
        
        Returns:
            dict: Serialized agent data
        
        Raises:
            ValueError: If serialization fails
        """
        pass
    
    def to_json(self, ir: AgentIR) -> str:
        """
        Convert AgentIR to JSON string.
        
        Args:
            ir: The AgentIR to convert
        
        Returns:
            str: JSON string representation
        """
        import json
        data = self.serialize(ir, 'json')
        return json.dumps(data, indent=2)
    
    def to_yaml(self, ir: AgentIR) -> str:
        """
        Convert AgentIR to YAML string.
        
        Args:
            ir: The AgentIR to convert
        
        Returns:
            str: YAML string representation
        """
        try:
            import yaml
            data = self.serialize(ir, 'yaml')
            return yaml.dump(data, default_flow_style=False, indent=2)
        except ImportError:
            raise ValueError("PyYAML is not installed. Install it with: pip install PyYAML")


# Import format-specific serializers
from .claude import ClaudeSerializer
from .roo import RooSerializer
from .custom import CustomSerializer

__all__ = [
    'BaseSerializer',
    'ClaudeSerializer',
    'RooSerializer',
    'CustomSerializer'
]