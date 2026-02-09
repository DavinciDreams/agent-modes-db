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

            # Set default values for tools and skills if not present
            if 'tools' not in data:
                data['tools'] = []
            if 'skills' not in data:
                data['skills'] = []

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

            # Set default values for tools and skills if not present
            if 'tools' not in data:
                data['tools'] = []
            if 'skills' not in data:
                data['skills'] = []

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
        Parse Markdown content with frontmatter and structured sections.

        Args:
            content: Markdown string to parse

        Returns:
            dict: Parsed data with frontmatter and extracted sections

        Raises:
            ValueError: If parsing fails
        """
        try:
            # Try to parse YAML frontmatter
            import yaml
            import re
            data = {}

            lines = content.split('\n')
            body_start = 0

            # Check for YAML frontmatter (delimited by ---)
            if lines[0].strip() == '---':
                # Find the closing ---
                frontmatter_lines = []

                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '---':
                        frontmatter = '\n'.join(frontmatter_lines)
                        data = yaml.safe_load(frontmatter) or {}
                        body_start = i + 1
                        break
                    frontmatter_lines.append(line)

            # Get body content (after frontmatter if present)
            body_content = '\n'.join(lines[body_start:]).strip()
            data['body'] = body_content

            # Extract structured sections from markdown headings
            sections = self._extract_sections(body_content)

            # Extract name from frontmatter or first heading
            if 'name' not in data:
                if sections.get('title'):
                    data['name'] = sections['title']
                else:
                    # Try to extract from first heading
                    for line in lines[body_start:]:
                        if line.startswith('#'):
                            data['name'] = line.lstrip('#').strip()
                            break

            # Extract description
            if 'description' not in data:
                if sections.get('description'):
                    data['description'] = sections['description']
                else:
                    data['description'] = body_content[:500]

            # Extract instructions
            if 'instructions' not in data and sections.get('instructions'):
                data['instructions'] = sections['instructions']

            # Extract tools as array
            if 'tools' not in data:
                if sections.get('tools'):
                    data['tools'] = self._parse_list_section(sections['tools'])
                else:
                    data['tools'] = []  # Default to empty list when no tools section

            # Extract skills as array
            if 'skills' not in data:
                if sections.get('skills'):
                    data['skills'] = self._parse_list_section(sections['skills'])
                else:
                    data['skills'] = []  # Default to empty list when no skills section

            return data
        except ImportError:
            raise ValueError("PyYAML is not installed. Install it with: pip install PyYAML")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in frontmatter: {str(e)}")

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from markdown content based on headings."""
        import re
        sections = {}

        # Split by headings (## or ###)
        heading_pattern = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)
        parts = heading_pattern.split(content)

        # First part is content before first heading (if any)
        if parts[0].strip():
            sections['preamble'] = parts[0].strip()

        # Process heading pairs
        current_heading = None
        for i in range(1, len(parts), 3):
            if i+1 < len(parts):
                heading_text = parts[i+1].strip().lower()
                content_text = parts[i+2].strip() if i+2 < len(parts) else ''

                # Map common heading names to section keys
                if heading_text in ['description', 'about', 'overview']:
                    sections['description'] = content_text
                elif heading_text in ['instructions', 'instruction', 'system prompt', 'prompt']:
                    sections['instructions'] = content_text
                elif heading_text in ['tools', 'tool']:
                    sections['tools'] = content_text
                elif heading_text in ['skills', 'skill', 'capabilities']:
                    sections['skills'] = content_text
                elif not sections.get('title') and parts[i].count('#') == 1:
                    # First H1 is the title
                    sections['title'] = parts[i+1].strip()

        return sections

    def _parse_list_section(self, content: str) -> list:
        """Parse a markdown list section into an array."""
        import re
        items = []

        # Match both - and * bullet points
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            # Match bullet points
            if line.startswith('- ') or line.startswith('* '):
                item = line[2:].strip()
                items.append(item)
            # Match numbered lists
            elif re.match(r'^\d+\.\s+', line):
                item = re.sub(r'^\d+\.\s+', '', line).strip()
                items.append(item)

        return items
    
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
