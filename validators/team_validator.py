"""
Team configuration validator

This module provides comprehensive validation for team configurations,
ensuring proper structure, agent references, and workflow definitions.
"""
import re
import json
from .agent_validator import SLUG_PATTERN


class TeamValidationError(Exception):
    """Raised when team validation fails"""
    def __init__(self, errors):
        self.errors = errors
        super().__init__(f"Team validation failed: {', '.join(errors)}")


VALID_WORKFLOW_TYPES = ['sequential', 'parallel', 'orchestrated']


def validate_team(config, agent_exists_fn=None):
    """
    Validate team configuration

    Args:
        config: Team configuration dict
        agent_exists_fn: Optional function to check if agent exists (slug -> bool)

    Returns:
        tuple: (is_valid: bool, errors: list)

    Example:
        >>> def check_agent(slug):
        ...     return slug in ['agent1', 'agent2']
        >>> is_valid, errors = validate_team({
        ...     'slug': 'dev-team',
        ...     'name': 'Development Team',
        ...     'agents': [
        ...         {'slug': 'agent1', 'role': 'developer'},
        ...         {'slug': 'agent2', 'role': 'reviewer'}
        ...     ]
        ... }, agent_exists_fn=check_agent)
        >>> print(is_valid)
        True
    """
    errors = []

    # Required fields
    required_fields = ['slug', 'name', 'agents']
    for field in required_fields:
        if not config.get(field):
            errors.append(f"Missing required field: {field}")

    # Slug validation
    slug = config.get('slug', '')
    if slug:
        if not SLUG_PATTERN.match(slug):
            errors.append("Slug must contain only lowercase letters, numbers, and hyphens")

        if len(slug) < 3:
            errors.append("Slug must be at least 3 characters")

        if len(slug) > 100:
            errors.append("Slug must be less than 100 characters")

    # Name validation
    name = config.get('name', '')
    if name:
        if len(name) > 255:
            errors.append("Name must be less than 255 characters")

        if len(name) < 2:
            errors.append("Name must be at least 2 characters")

    # Description validation (optional)
    description = config.get('description', '')
    if description and len(description) > 1000:
        errors.append("Description must be less than 1000 characters")

    # Agents validation
    agents = config.get('agents', [])
    if not isinstance(agents, list):
        errors.append("Agents must be an array")
    else:
        if len(agents) == 0:
            errors.append("Team must have at least one agent")

        if len(agents) > 50:
            errors.append("Team cannot have more than 50 agents")

        agent_slugs = []
        for i, agent in enumerate(agents):
            if not isinstance(agent, dict):
                errors.append(f"Agent at index {i} must be an object")
                continue

            # Required agent fields
            if 'slug' not in agent:
                errors.append(f"Agent at index {i} missing 'slug' field")
            else:
                agent_slug = agent['slug']
                agent_slugs.append(agent_slug)

                # Validate agent slug format
                if not SLUG_PATTERN.match(agent_slug):
                    errors.append(f"Agent at index {i} has invalid slug format: '{agent_slug}'")

                # Check if agent exists (if function provided)
                if agent_exists_fn and not agent_exists_fn(agent_slug):
                    errors.append(f"Agent '{agent_slug}' does not exist")

            # Optional but recommended fields
            if 'role' not in agent:
                errors.append(f"Agent at index {i} should have a 'role' field")
            else:
                role = agent['role']
                if not isinstance(role, str):
                    errors.append(f"Agent at index {i} role must be a string")
                elif len(role) > 100:
                    errors.append(f"Agent at index {i} role must be less than 100 characters")

            # Validate priority if present
            if 'priority' in agent:
                priority = agent['priority']
                if not isinstance(priority, int) or priority < 0 or priority > 100:
                    errors.append(f"Agent at index {i} priority must be an integer between 0 and 100")

        # Check for duplicate agents
        if len(agent_slugs) != len(set(agent_slugs)):
            duplicates = [slug for slug in agent_slugs if agent_slugs.count(slug) > 1]
            errors.append(f"Duplicate agents in team: {', '.join(set(duplicates))}")

    # Orchestrator validation
    orchestrator = config.get('orchestrator')
    if orchestrator:
        if not isinstance(orchestrator, str):
            errors.append("Orchestrator must be a string (agent slug)")
        else:
            if not SLUG_PATTERN.match(orchestrator):
                errors.append(f"Orchestrator has invalid slug format: '{orchestrator}'")

            if agent_exists_fn and not agent_exists_fn(orchestrator):
                errors.append(f"Orchestrator agent '{orchestrator}' does not exist")

            # Check if orchestrator is in the team
            agents = config.get('agents', [])
            orchestrator_in_team = any(a.get('slug') == orchestrator for a in agents if isinstance(a, dict))
            if not orchestrator_in_team:
                errors.append(f"Orchestrator agent '{orchestrator}' must be part of the team")

    # Workflow validation
    workflow = config.get('workflow', {})
    if workflow:
        if not isinstance(workflow, dict):
            errors.append("Workflow must be an object")
        else:
            workflow_type = workflow.get('type')
            if workflow_type:
                if workflow_type not in VALID_WORKFLOW_TYPES:
                    errors.append(f"Invalid workflow type: '{workflow_type}'. Valid types: {', '.join(VALID_WORKFLOW_TYPES)}")

            # Validate stages if present
            stages = workflow.get('stages', [])
            if stages:
                if not isinstance(stages, list):
                    errors.append("Workflow stages must be an array")
                else:
                    for i, stage in enumerate(stages):
                        if not isinstance(stage, dict):
                            errors.append(f"Workflow stage at index {i} must be an object")
                            continue

                        # Validate stage name
                        if 'name' not in stage:
                            errors.append(f"Workflow stage at index {i} missing 'name' field")
                        elif len(stage['name']) > 100:
                            errors.append(f"Workflow stage at index {i} name must be less than 100 characters")

                        # Validate stage agents
                        if 'agents' in stage:
                            stage_agents = stage['agents']
                            if not isinstance(stage_agents, list):
                                errors.append(f"Workflow stage at index {i} agents must be an array")
                            else:
                                # Check that stage agents are in the team
                                team_agent_slugs = [a.get('slug') for a in config.get('agents', []) if isinstance(a, dict)]
                                for stage_agent in stage_agents:
                                    if stage_agent not in team_agent_slugs:
                                        errors.append(f"Workflow stage at index {i} references unknown agent: '{stage_agent}'")

    # Max concurrent tasks validation (optional)
    max_concurrent = config.get('max_concurrent_tasks')
    if max_concurrent is not None:
        if not isinstance(max_concurrent, int) or max_concurrent < 1 or max_concurrent > 100:
            errors.append("max_concurrent_tasks must be an integer between 1 and 100")

    # Timeout validation (optional)
    timeout = config.get('timeout')
    if timeout is not None:
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            errors.append("timeout must be a positive number")

    return len(errors) == 0, errors


def validate_team_strict(config, agent_exists_fn=None):
    """
    Validate team and raise exception if invalid

    Args:
        config: Team configuration dict
        agent_exists_fn: Optional function to check if agent exists (slug -> bool)

    Returns:
        bool: True if valid

    Raises:
        TeamValidationError: If validation fails with list of errors

    Example:
        >>> try:
        ...     validate_team_strict({'slug': 'test'})
        ... except TeamValidationError as e:
        ...     print(e.errors)
        ['Missing required field: name', ...]
    """
    is_valid, errors = validate_team(config, agent_exists_fn)
    if not is_valid:
        raise TeamValidationError(errors)
    return True


def validate_team_json(json_string, agent_exists_fn=None):
    """
    Validate team from JSON string

    Args:
        json_string: JSON string to parse and validate
        agent_exists_fn: Optional function to check if agent exists (slug -> bool)

    Returns:
        tuple: (is_valid: bool, errors: list)
    """
    errors = []

    # Parse JSON
    try:
        config = json.loads(json_string)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {str(e)}")
        return False, errors

    # Validate config
    is_valid, validation_errors = validate_team(config, agent_exists_fn)
    errors.extend(validation_errors)

    return is_valid, errors


# Export validation rules for external use
__all__ = [
    'validate_team',
    'validate_team_strict',
    'validate_team_json',
    'TeamValidationError',
    'VALID_WORKFLOW_TYPES'
]
