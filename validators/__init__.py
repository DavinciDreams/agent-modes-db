"""
Validation system for agents and teams

This module provides comprehensive validation for agent and team configurations,
ensuring data integrity and conformance to the Agent Modes Database specification.

Usage:
    >>> from validators import validate_agent, validate_team
    >>> is_valid, errors = validate_agent({
    ...     'slug': 'code-helper',
    ...     'name': 'Code Helper',
    ...     'instructions': 'You are a helpful coding assistant...',
    ...     'tools': ['Read', 'Write']
    ... })
    >>> if not is_valid:
    ...     print("Validation errors:", errors)

    >>> from validators import AgentValidationError, validate_agent_strict
    >>> try:
    ...     validate_agent_strict(config)
    ... except AgentValidationError as e:
    ...     print("Invalid agent:", e.errors)
"""

from .agent_validator import (
    validate_agent,
    validate_agent_strict,
    validate_agent_json,
    AgentValidationError,
    VALID_TOOLS,
    VALID_MODELS,
    SLUG_PATTERN
)

from .team_validator import (
    validate_team,
    validate_team_strict,
    validate_team_json,
    TeamValidationError,
    VALID_WORKFLOW_TYPES
)

__all__ = [
    # Agent validation
    'validate_agent',
    'validate_agent_strict',
    'validate_agent_json',
    'AgentValidationError',
    'VALID_TOOLS',
    'VALID_MODELS',

    # Team validation
    'validate_team',
    'validate_team_strict',
    'validate_team_json',
    'TeamValidationError',
    'VALID_WORKFLOW_TYPES',

    # Common
    'SLUG_PATTERN'
]

__version__ = '1.0.0'
