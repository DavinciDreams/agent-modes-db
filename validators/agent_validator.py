"""
Agent configuration validator

This module provides comprehensive validation for agent configurations,
ensuring all required fields are present and valid according to the
Agent Modes Database specification.
"""
import re
import json


class AgentValidationError(Exception):
    """Raised when agent validation fails"""
    def __init__(self, errors):
        self.errors = errors
        super().__init__(f"Agent validation failed: {', '.join(errors)}")


# Valid values
VALID_TOOLS = ['Read', 'Write', 'Edit', 'Glob', 'Grep', 'Bash', 'Task', 'TodoWrite']
VALID_MODELS = ['sonnet', 'haiku', 'opus']
SLUG_PATTERN = re.compile(r'^[a-z0-9-]+$')


def validate_agent(config):
    """
    Validate agent configuration

    Args:
        config: Agent configuration dict

    Returns:
        tuple: (is_valid: bool, errors: list)

    Example:
        >>> is_valid, errors = validate_agent({
        ...     'slug': 'code-analyzer',
        ...     'name': 'Code Analyzer',
        ...     'instructions': 'You are a code analyzer that helps...',
        ...     'tools': ['Read', 'Grep']
        ... })
        >>> print(is_valid)
        True
    """
    errors = []

    # Required fields
    required_fields = ['slug', 'name', 'instructions', 'tools']
    for field in required_fields:
        if not config.get(field):
            errors.append(f"Missing required field: {field}")

    # Slug format validation
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
    if name and len(name) > 255:
        errors.append("Name must be less than 255 characters")

    if name and len(name) < 2:
        errors.append("Name must be at least 2 characters")

    # Instructions validation
    instructions = config.get('instructions', '')
    if instructions and len(instructions) < 50:
        errors.append("Instructions must be at least 50 characters (provide meaningful guidance)")

    if instructions and len(instructions) > 10000:
        errors.append("Instructions must be less than 10000 characters")

    # Tools validation
    tools = config.get('tools', [])
    if not isinstance(tools, list):
        errors.append("Tools must be an array")
    else:
        if len(tools) == 0:
            errors.append("At least one tool is required")

        for tool in tools:
            if tool not in VALID_TOOLS:
                errors.append(f"Invalid tool: '{tool}'. Valid tools: {', '.join(VALID_TOOLS)}")

    # Skills validation (optional)
    skills = config.get('skills', [])
    if skills is not None and not isinstance(skills, list):
        errors.append("Skills must be an array")

    # Model validation
    model = config.get('default_model', 'sonnet')
    if model not in VALID_MODELS:
        errors.append(f"Invalid model: '{model}'. Valid models: {', '.join(VALID_MODELS)}")

    # Max turns validation
    max_turns = config.get('max_turns', 50)
    if not isinstance(max_turns, int) or max_turns < 1 or max_turns > 1000:
        errors.append("max_turns must be an integer between 1 and 1000")

    # Allowed edit patterns validation (optional)
    patterns = config.get('allowed_edit_patterns', [])
    if patterns is not None and not isinstance(patterns, list):
        errors.append("allowed_edit_patterns must be an array")
    else:
        # Validate regex patterns
        for pattern in patterns:
            if not isinstance(pattern, str):
                errors.append(f"allowed_edit_patterns must contain strings, found: {type(pattern).__name__}")
            else:
                try:
                    re.compile(pattern)
                except re.error as e:
                    errors.append(f"Invalid regex pattern '{pattern}': {str(e)}")

    # Description validation (optional but recommended)
    description = config.get('description', '')
    if description and len(description) > 1000:
        errors.append("Description must be less than 1000 characters")

    # Category validation (optional)
    category = config.get('category', '')
    if category and len(category) > 100:
        errors.append("Category must be less than 100 characters")

    return len(errors) == 0, errors


def validate_agent_strict(config):
    """
    Validate agent and raise exception if invalid

    Args:
        config: Agent configuration dict

    Returns:
        bool: True if valid

    Raises:
        AgentValidationError: If validation fails with list of errors

    Example:
        >>> try:
        ...     validate_agent_strict({'slug': 'test'})
        ... except AgentValidationError as e:
        ...     print(e.errors)
        ['Missing required field: name', ...]
    """
    is_valid, errors = validate_agent(config)
    if not is_valid:
        raise AgentValidationError(errors)
    return True


def validate_agent_json(json_string):
    """
    Validate agent from JSON string

    Args:
        json_string: JSON string to parse and validate

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
    is_valid, validation_errors = validate_agent(config)
    errors.extend(validation_errors)

    return is_valid, errors


# Export validation rules for external use
__all__ = [
    'validate_agent',
    'validate_agent_strict',
    'validate_agent_json',
    'AgentValidationError',
    'VALID_TOOLS',
    'VALID_MODELS',
    'SLUG_PATTERN'
]
