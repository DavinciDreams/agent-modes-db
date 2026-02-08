"""
Parsers module for agent definition file formats.

This module provides base parser classes and format detection
for parsing agent definition files in various formats (JSON, YAML, MD).
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional


class BaseParser(ABC):
    """
    Abstract base class for agent definition parsers.
    
    All format-specific parsers should inherit from this class
    and implement the parse() method.
    """
    
    @abstractmethod
    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse agent definition content.
        
        Args:
            content: The content to parse (string representation)
        
        Returns:
            dict: Parsed agent data
        
        Raises:
            ValueError: If parsing fails
        """
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, list]:
        """
        Validate parsed agent data.
        
        Args:
            data: The parsed data to validate
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        pass


class JSONParser(BaseParser):
    """Parser for JSON format agent definitions."""
    
    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse JSON content.
        
        Args:
            content: JSON string to parse
        
        Returns:
            dict: Parsed JSON data
        
        Raises:
            ValueError: If JSON is invalid
        """
        import json
        try:
            data = json.loads(content)
            if not isinstance(data, dict):
                raise ValueError("JSON content must be an object/dictionary")
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, list]:
        """
        Validate JSON agent data.
        
        Args:
            data: Parsed JSON data
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        # Basic validation - check for common agent fields
        if 'name' not in data:
            errors.append("Missing required field: 'name'")
        if 'description' not in data:
            errors.append("Missing required field: 'description'")
        
        # Check for at least one of the following fields
        has_agent_fields = any(field in data for field in ['system_prompt', 'capabilities', 'tools'])
        if not has_agent_fields:
            errors.append("Missing agent-specific fields (need at least one of: system_prompt, capabilities, tools)")
        
        return len(errors) == 0, errors


class YAMLParser(BaseParser):
    """Parser for YAML format agent definitions."""
    
    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse YAML content.
        
        Args:
            content: YAML string to parse
        
        Returns:
            dict: Parsed YAML data
        
        Raises:
            ValueError: If YAML is invalid
        """
        try:
            import yaml
            data = yaml.safe_load(content)
            if not isinstance(data, dict):
                raise ValueError("YAML content must be a dictionary/object")
            return data
        except ImportError:
            raise ValueError("PyYAML is not installed. Install it with: pip install PyYAML")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {str(e)}")
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, list]:
        """
        Validate YAML agent data.
        
        Args:
            data: Parsed YAML data
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        # Basic validation - check for common agent fields
        if 'name' not in data:
            errors.append("Missing required field: 'name'")
        if 'description' not in data:
            errors.append("Missing required field: 'description'")
        
        # Check for at least one of the following fields
        has_agent_fields = any(field in data for field in ['system_prompt', 'capabilities', 'tools'])
        if not has_agent_fields:
            errors.append("Missing agent-specific fields (need at least one of: system_prompt, capabilities, tools)")
        
        return len(errors) == 0, errors


class MarkdownParser(BaseParser):
    """Parser for Markdown format agent definitions."""
    
    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse Markdown content with frontmatter.
        
        Args:
            content: Markdown string to parse
        
        Returns:
            dict: Parsed data with frontmatter as metadata and body as description
        
        Raises:
            ValueError: If parsing fails
        """
        try:
            # Try to parse YAML frontmatter
            import yaml
            data = {}
            
            lines = content.split('\n')
            
            # Check for YAML frontmatter (delimited by ---)
            if lines[0].strip() == '---':
                # Find the closing ---
                frontmatter_lines = []
                body_lines = []
                in_frontmatter = False
                
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '---':
                        in_frontmatter = True
                        body_lines = lines[i+1:]
                        break
                    frontmatter_lines.append(line)
                
                if in_frontmatter:
                    frontmatter = '\n'.join(frontmatter_lines)
                    data = yaml.safe_load(frontmatter) or {}
                    data['body'] = '\n'.join(body_lines).strip()
                else:
                    # No closing --- found, treat entire content as body
                    data['body'] = content.strip()
            else:
                # No frontmatter, treat entire content as body
                data['body'] = content.strip()
            
            # Extract name from frontmatter or generate from body
            if 'name' not in data:
                # Try to extract name from first heading
                for line in lines:
                    if line.startswith('#'):
                        data['name'] = line.lstrip('#').strip()
                        break
                if 'name' not in data:
                    # Use first line of body as name
                    first_line = data.get('body', '').split('\n')[0]
                    data['name'] = first_line[:50] + ('...' if len(first_line) > 50 else '')
            
            # Use body as description if not provided
            if 'description' not in data:
                data['description'] = data.get('body', '')
            
            return data
        except ImportError:
            raise ValueError("PyYAML is not installed. Install it with: pip install PyYAML")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in frontmatter: {str(e)}")
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, list]:
        """
        Validate Markdown agent data.
        
        Args:
            data: Parsed Markdown data
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        if 'name' not in data:
            errors.append("Missing required field: 'name'")
        
        if 'description' not in data and 'body' not in data:
            errors.append("Missing required field: 'description' or 'body'")
        
        return len(errors) == 0, errors


def detect_format(filename: str, content: str = None) -> str:
    """
    Detect file format based on filename extension and optionally content.
    
    Args:
        filename: The filename to analyze
        content: Optional file content for additional detection
    
    Returns:
        str: Detected format ('json', 'yaml', 'md', or 'unknown')
    """
    # Get file extension
    _, ext = os.path.splitext(filename.lower())
    
    # Map extensions to formats
    extension_map = {
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'md',
        '.markdown': 'md'
    }
    
    # Detect from extension
    file_format = extension_map.get(ext, 'unknown')
    
    # If unknown and content is provided, try to detect from content
    if file_format == 'unknown' and content:
        # Try to detect JSON
        try:
            import json
            json.loads(content.strip())
            return 'json'
        except:
            pass
        
        # Try to detect YAML
        try:
            import yaml
            yaml.safe_load(content.strip())
            return 'yaml'
        except:
            pass
    
    return file_format


def detect_agent_format(content: str) -> str:
    """
    Detect agent format (claude, roo, custom) from content.
    
    Args:
        content: The content to analyze
    
    Returns:
        str: Detected agent format ('claude', 'roo', 'custom', or 'unknown')
    """
    content_lower = content.lower()
    
    # Check for Roo format indicators
    if 'mode:' in content or 'icon:' in content:
        return 'roo'
    
    # Check for custom format indicators
    if 'config_schema' in content:
        return 'custom'
    
    # Default to Claude format
    return 'claude'


def get_parser(format: str) -> BaseParser:
    """
    Get the appropriate parser for a given format.
    
    Args:
        format: The format ('json', 'yaml', 'md')
    
    Returns:
        BaseParser: Parser instance for the format
    
    Raises:
        ValueError: If format is not supported
    """
    parsers = {
        'json': JSONParser(),
        'yaml': YAMLParser(),
        'yml': YAMLParser(),
        'md': MarkdownParser(),
        'markdown': MarkdownParser()
    }
    
    parser = parsers.get(format.lower())
    if not parser:
        raise ValueError(f"Unsupported format: {format}. Supported formats: {', '.join(parsers.keys())}")
    
    return parser


def parse_to_ir(content: str, agent_format: str = None) -> 'AgentIR':
    """
    Parse content to AgentIR using format-specific parser.
    
    Args:
        content: The content to parse
        agent_format: The agent format ('claude', 'roo', 'custom'). If None, will auto-detect.
    
    Returns:
        AgentIR: Parsed agent data as intermediate representation
    
    Raises:
        ValueError: If parsing fails
    """
    # Auto-detect format if not provided
    if not agent_format:
        agent_format = detect_agent_format(content)
    
    # Get format-specific parser
    if agent_format == 'claude':
        from .claude import ClaudeParser
        parser = ClaudeParser()
    elif agent_format == 'roo':
        from .roo import RooParser
        parser = RooParser()
    elif agent_format == 'custom':
        from .custom import CustomParser
        parser = CustomParser()
    else:
        raise ValueError(f"Unsupported agent format: {agent_format}")
    
    # Parse and return IR
    return parser.parse(content)


# Import format-specific parsers
from .claude import ClaudeParser
from .roo import RooParser
from .custom import CustomParser

# Export main classes and functions
__all__ = [
    'BaseParser',
    'JSONParser',
    'YAMLParser',
    'MarkdownParser',
    'ClaudeParser',
    'RooParser',
    'CustomParser',
    'detect_format',
    'detect_agent_format',
    'get_parser',
    'parse_to_ir'
]
