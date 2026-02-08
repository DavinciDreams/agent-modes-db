"""
Agent Card Generator

This module provides functionality for generating agent cards
following Microsoft's agent discovery standards.
"""

import json
import yaml
from typing import Dict, Any, Optional, List


class AgentCardGenerator:
    """
    Generate agent cards for Microsoft discoverability
    
    This class provides methods to generate agent cards from various
    entity types (templates, configurations, custom agents) following
    Microsoft's agent discovery schema.
    """
    
    SCHEMA_VERSION = "1.0"
    SCHEMA_URL = "https://agent-discovery.microsoft.com/v1"
    
    # Required fields for validation
    REQUIRED_FIELDS = ['id', 'name', 'description', 'version', 'category']
    
    @classmethod
    def generate_from_template(cls, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate agent card from template data
        
        Args:
            template_data: Dictionary containing template data with keys:
                - id: Template ID
                - name: Template name
                - description: Template description
                - category: Template category
                - created_at: Creation timestamp
                - updated_at: Update timestamp
        
        Returns:
            Dictionary containing the agent card
        """
        return {
            "$schema": cls.SCHEMA_URL,
            "agent": {
                "id": f"template-{template_data['id']}",
                "name": template_data['name'],
                "description": template_data['description'],
                "version": "1.0.0",
                "category": template_data['category'],
                "capabilities": [],
                "tools": [],
                "author": {
                    "name": "Agent Modes DB",
                    "url": "https://github.com/agent-modes-db"
                },
                "metadata": {
                    "created_at": template_data.get('created_at', ''),
                    "updated_at": template_data.get('updated_at', ''),
                    "tags": [template_data['category'].lower()],
                    "language": "en",
                    "license": "MIT"
                },
                "compatibility": {
                    "platforms": ["web"]
                }
            }
        }
    
    @classmethod
    def generate_from_configuration(cls, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate agent card from configuration data
        
        Args:
            config_data: Dictionary containing configuration data with keys:
                - id: Configuration ID
                - name: Configuration name
                - config_json: Configuration JSON string or dict
                - template_name: Template name (optional)
                - created_at: Creation timestamp
                - updated_at: Update timestamp
        
        Returns:
            Dictionary containing the agent card
        """
        capabilities = []
        tools = []
        
        try:
            config_json = config_data['config_json']
            if isinstance(config_json, str):
                config_dict = json.loads(config_json)
            else:
                config_dict = config_json
            
            capabilities = config_dict.get('capabilities', [])
            tools = config_dict.get('tools', [])
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        
        return {
            "$schema": cls.SCHEMA_URL,
            "agent": {
                "id": f"configuration-{config_data['id']}",
                "name": config_data['name'],
                "description": f"Configuration based on {config_data.get('template_name', 'custom')}",
                "version": "1.0.0",
                "category": "Configuration",
                "capabilities": capabilities,
                "tools": tools,
                "author": {
                    "name": "Agent Modes DB"
                },
                "metadata": {
                    "created_at": config_data.get('created_at', ''),
                    "updated_at": config_data.get('updated_at', ''),
                    "tags": ["configuration"],
                    "language": "en"
                },
                "compatibility": {
                    "platforms": ["web"]
                }
            }
        }
    
    @classmethod
    def generate_from_custom_agent(cls, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate agent card from custom agent data
        
        Args:
            agent_data: Dictionary containing agent data with keys:
                - id: Agent ID
                - name: Agent name
                - description: Agent description
                - capabilities: Capabilities list or JSON string
                - tools: Tools list or JSON string
                - created_at: Creation timestamp
                - updated_at: Update timestamp
        
        Returns:
            Dictionary containing the agent card
        """
        capabilities = []
        tools = []
        
        # Parse capabilities
        if isinstance(agent_data.get('capabilities'), str):
            try:
                capabilities = json.loads(agent_data['capabilities'])
            except json.JSONDecodeError:
                capabilities = []
        elif isinstance(agent_data.get('capabilities'), list):
            capabilities = agent_data['capabilities']
        
        # Parse tools
        if isinstance(agent_data.get('tools'), str):
            try:
                tools = json.loads(agent_data['tools'])
            except json.JSONDecodeError:
                tools = []
        elif isinstance(agent_data.get('tools'), list):
            tools = agent_data['tools']
        
        return {
            "$schema": cls.SCHEMA_URL,
            "agent": {
                "id": f"custom-agent-{agent_data['id']}",
                "name": agent_data['name'],
                "description": agent_data['description'],
                "version": "1.0.0",
                "category": "Custom",
                "capabilities": capabilities,
                "tools": tools,
                "author": {
                    "name": "Agent Modes DB"
                },
                "metadata": {
                    "created_at": agent_data.get('created_at', ''),
                    "updated_at": agent_data.get('updated_at', ''),
                    "tags": ["custom"],
                    "language": "en"
                },
                "compatibility": {
                    "platforms": ["web"]
                }
            }
        }
    
    @classmethod
    def generate_from_ir(cls, agent_ir: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate agent card from AgentIR (Intermediate Representation)
        
        Args:
            agent_ir: Dictionary containing AgentIR data with keys:
                - id: Agent ID
                - name: Agent name
                - description: Agent description
                - category: Agent category
                - capabilities: Capabilities list
                - tools: Tools list
                - author: Author information (optional)
                - metadata: Additional metadata (optional)
                - compatibility: Compatibility information (optional)
        
        Returns:
            Dictionary containing the agent card
        """
        return {
            "$schema": cls.SCHEMA_URL,
            "agent": {
                "id": agent_ir.get('id', 'unknown'),
                "name": agent_ir.get('name', 'Unknown Agent'),
                "description": agent_ir.get('description', ''),
                "version": agent_ir.get('version', '1.0.0'),
                "category": agent_ir.get('category', 'General'),
                "capabilities": agent_ir.get('capabilities', []),
                "tools": agent_ir.get('tools', []),
                "author": agent_ir.get('author', {
                    "name": "Agent Modes DB"
                }),
                "metadata": agent_ir.get('metadata', {
                    "tags": [],
                    "language": "en",
                    "license": "MIT"
                }),
                "compatibility": agent_ir.get('compatibility', {
                    "platforms": ["web"]
                })
            }
        }
    
    @classmethod
    def validate_card(cls, card_data: Dict[str, Any]) -> tuple[bool, Optional[List[str]]]:
        """
        Validate agent card against schema
        
        Args:
            card_data: Dictionary containing the agent card
        
        Returns:
            Tuple of (is_valid, errors) where errors is a list of validation error messages
        """
        errors = []
        
        # Check if agent key exists
        if 'agent' not in card_data:
            errors.append("Missing 'agent' key in card data")
            return False, errors
        
        agent = card_data['agent']
        
        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if field not in agent:
                errors.append(f"Missing required field: agent.{field}")
            elif not agent[field]:
                errors.append(f"Required field cannot be empty: agent.{field}")
        
        # Validate schema URL
        if '$schema' in card_data:
            if card_data['$schema'] != cls.SCHEMA_URL:
                errors.append(f"Invalid schema URL. Expected: {cls.SCHEMA_URL}")
        
        # Validate version format (semantic version)
        if 'version' in agent:
            version = agent['version']
            if not isinstance(version, str) or not version.replace('.', '').isdigit():
                errors.append(f"Invalid version format: {version}. Expected semantic version (e.g., 1.0.0)")
        
        return len(errors) == 0, errors if errors else None
    
    @classmethod
    def export_card(cls, card_data: Dict[str, Any], format: str = 'json') -> str:
        """
        Export agent card in specified format
        
        Args:
            card_data: Dictionary containing the agent card
            format: Export format ('json' or 'yaml')
        
        Returns:
            String containing the exported card data
        
        Raises:
            ValueError: If format is not supported
        """
        if format.lower() == 'json':
            return json.dumps(card_data, indent=2)
        elif format.lower() in ['yaml', 'yml']:
            return yaml.dump(card_data, default_flow_style=False, sort_keys=False)
        else:
            raise ValueError(f"Unsupported export format: {format}. Supported formats: json, yaml")
    
    @classmethod
    def import_card(cls, card_data: str, format: str = 'json') -> Dict[str, Any]:
        """
        Import agent card from string
        
        Args:
            card_data: String containing the agent card
            format: Import format ('json' or 'yaml')
        
        Returns:
            Dictionary containing the imported card data
        
        Raises:
            ValueError: If format is not supported or parsing fails
        """
        if format.lower() == 'json':
            return json.loads(card_data)
        elif format.lower() in ['yaml', 'yml']:
            return yaml.safe_load(card_data)
        else:
            raise ValueError(f"Unsupported import format: {format}. Supported formats: json, yaml")
