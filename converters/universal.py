"""
Universal converter for agent format transformations.

This module provides the UniversalConverter class for converting
agent definitions between different formats (Claude, Roo, Custom).
"""

import json
from typing import Dict, Any, Tuple, List, Optional
from .ir import AgentIR
from parsers.claude import ClaudeParser
from parsers.roo import RooParser
from parsers.custom import CustomParser
from parsers import JSONParser, YAMLParser
from serializers.claude import ClaudeSerializer
from serializers.roo import RooSerializer
from serializers.custom import CustomSerializer


class UniversalConverter:
    """Universal converter between agent formats."""
    
    # Registry of available parsers
    PARSERS = {
        'claude': ClaudeParser(),
        'roo': RooParser(),
        'custom': CustomParser()
    }
    
    # Registry of available serializers
    SERIALIZERS = {
        'claude': ClaudeSerializer(),
        'roo': RooSerializer(),
        'custom': CustomSerializer()
    }
    
    # File format parsers
    FILE_PARSERS = {
        'json': JSONParser(),
        'yaml': YAMLParser(),
        'yml': YAMLParser()
    }
    
    @classmethod
    def convert(cls, source_data: Dict[str, Any], source_format: str, target_format: str) -> Tuple[Dict[str, Any], List[str]]:
        """
        Convert agent data from source format to target format.
        
        Args:
            source_data: Source agent data as dictionary
            source_format: Source format ('claude', 'roo', 'custom')
            target_format: Target format ('claude', 'roo', 'custom')
        
        Returns:
            tuple: (converted_data, warnings)
        
        Raises:
            ValueError: If conversion fails
        """
        warnings = []
        
        # Validate formats
        if source_format not in cls.PARSERS:
            raise ValueError(f"Unsupported source format: {source_format}. Supported formats: {', '.join(cls.PARSERS.keys())}")
        
        if target_format not in cls.SERIALIZERS:
            raise ValueError(f"Unsupported target format: {target_format}. Supported formats: {', '.join(cls.SERIALIZERS.keys())}")
        
        # Parse source data to IR
        parser = cls.PARSERS[source_format]
        
        # Validate source data
        is_valid, errors = parser.validate(source_data)
        if not is_valid:
            raise ValueError(f"Invalid source data: {', '.join(errors)}")
        
        # Convert to IR
        ir = parser.parse(json.dumps(source_data))
        
        # Handle field mappings and defaults
        conversion_warnings = cls._handle_field_mapping(ir, source_format, target_format)
        warnings.extend(conversion_warnings)
        
        # Serialize IR to target format
        serializer = cls.SERIALIZERS[target_format]
        target_data = serializer.serialize(ir)
        
        return target_data, warnings
    
    @classmethod
    def convert_file(cls, file_path: str, source_format: str, target_format: str) -> Tuple[Dict[str, Any], List[str]]:
        """
        Convert agent definition from file to target format.
        
        Args:
            file_path: Path to the source file
            source_format: Source format ('claude', 'roo', 'custom', 'json', 'yaml')
            target_format: Target format ('claude', 'roo', 'custom')
        
        Returns:
            tuple: (converted_data, warnings)
        
        Raises:
            ValueError: If conversion fails
            FileNotFoundError: If file doesn't exist
        """
        import os
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return cls.convert_content(content, source_format, target_format)
    
    @classmethod
    def convert_content(cls, content: str, source_format: str, target_format: str) -> Tuple[Dict[str, Any], List[str]]:
        """
        Convert agent definition from content to target format.
        
        Args:
            content: Source content as string
            source_format: Source format ('claude', 'roo', 'custom', 'json', 'yaml')
            target_format: Target format ('claude', 'roo', 'custom')
        
        Returns:
            tuple: (converted_data, warnings)
        
        Raises:
            ValueError: If conversion fails
        """
        warnings = []
        
        # If source format is a file format (json/yaml), detect agent format
        if source_format in cls.FILE_PARSERS:
            # Parse file content first
            file_parser = cls.FILE_PARSERS[source_format]
            source_data = file_parser.parse(content)
            
            # Detect agent format from content
            agent_format = cls._detect_agent_format(content)
            warnings.append(f"Detected agent format: {agent_format}")
            
            # Convert using detected agent format
            return cls.convert(source_data, agent_format, target_format)
        else:
            # Parse content as JSON/YAML based on source format
            try:
                import json
                source_data = json.loads(content)
            except json.JSONDecodeError:
                try:
                    import yaml
                    source_data = yaml.safe_load(content)
                except ImportError:
                    raise ValueError("PyYAML is not installed. Install it with: pip install PyYAML")
                except yaml.YAMLError as e:
                    raise ValueError(f"Invalid YAML: {str(e)}")
            
            return cls.convert(source_data, source_format, target_format)
    
    @classmethod
    def get_supported_formats(cls) -> Dict[str, Dict[str, str]]:
        """
        Get list of supported formats.
        
        Returns:
            dict: Dictionary of supported formats with descriptions
        """
        formats = {}
        
        # Agent formats
        for format_name, parser in cls.PARSERS.items():
            formats[format_name] = {
                'name': format_name.title(),
                'description': parser.get_format_description(),
                'type': 'agent'
            }
        
        # Add custom format (serializer only)
        if 'custom' in cls.SERIALIZERS:
            formats['custom'] = {
                'name': 'Custom',
                'description': cls.SERIALIZERS['custom'].get_format_description(),
                'type': 'agent'
            }
        
        # File formats
        for format_name in cls.FILE_PARSERS.keys():
            formats[format_name] = {
                'name': format_name.upper(),
                'description': f"{format_name.upper()} file format",
                'type': 'file'
            }
        
        return formats
    
    @classmethod
    def validate_conversion(cls, source_format: str, target_format: str) -> Tuple[bool, List[str]]:
        """
        Validate if conversion between formats is supported.
        
        Args:
            source_format: Source format
            target_format: Target format
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check source format
        if source_format not in cls.PARSERS and source_format not in cls.FILE_PARSERS:
            errors.append(f"Unsupported source format: {source_format}")
        
        # Check target format
        if target_format not in cls.SERIALIZERS:
            errors.append(f"Unsupported target format: {target_format}")
        
        # Check if same format
        if source_format == target_format:
            errors.append("Source and target formats are the same")
        
        return len(errors) == 0, errors
    
    @classmethod
    def _handle_field_mapping(cls, ir: AgentIR, source: str, target: str) -> List[str]:
        """
        Handle field mappings and add defaults for missing fields.
        
        Args:
            ir: AgentIR instance
            source: Source format
            target: Target format
        
        Returns:
            list: List of warnings
        """
        warnings = []
        
        # Add default icon for Roo format if missing
        if target == 'roo' and not ir.icon:
            ir.icon = 'fa-robot'
            warnings.append("Field 'icon' was added with default value 'fa-robot'")
        
        # Add default category for Roo format if missing
        if target == 'roo' and not ir.category:
            ir.category = 'general'
            warnings.append("Field 'category' was added with default value 'general'")
        
        # Add default tags for Roo format if missing
        if target == 'roo' and not ir.tags:
            ir.tags = []
            warnings.append("Field 'tags' was initialized as empty array")
        
        # Add default capabilities for Custom format if missing
        if target == 'custom' and not ir.capabilities:
            ir.capabilities = []
            warnings.append("Field 'capabilities' was initialized as empty array")
        
        # Add default tools for Custom format if missing
        if target == 'custom' and not ir.tools:
            ir.tools = []
            warnings.append("Field 'tools' was initialized as empty array")
        
        # Add default system_prompt for Custom format if missing
        if target == 'custom' and not ir.system_prompt:
            ir.system_prompt = f"You are {ir.name}, an AI assistant. {ir.description}"
            warnings.append("Field 'system_prompt' was generated from name and description")
        
        return warnings
    
    @classmethod
    def _detect_agent_format(cls, content: str) -> str:
        """
        Detect agent format from content.
        
        Args:
            content: Content to analyze
        
        Returns:
            str: Detected agent format ('claude', 'roo', 'custom')
        """
        content_lower = content.lower()
        
        # Check for Roo format indicators
        if 'mode:' in content_lower or 'icon:' in content_lower:
            return 'roo'
        
        # Check for custom format indicators
        if 'config_schema' in content_lower:
            return 'custom'
        
        # Default to Claude format
        return 'claude'