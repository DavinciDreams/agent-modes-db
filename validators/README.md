# Validators Module

Comprehensive validation system for agent and team configurations.

## Installation

No additional dependencies required. The validators module uses only Python standard library.

## Quick Start

```python
from validators import validate_agent, validate_team

# Validate an agent
agent_config = {
    'slug': 'code-helper',
    'name': 'Code Helper',
    'instructions': 'You are a helpful coding assistant that helps developers write better code.',
    'tools': ['Read', 'Write', 'Edit']
}

is_valid, errors = validate_agent(agent_config)
if not is_valid:
    print("Validation errors:", errors)
```

## Agent Validation

### Basic Validation

```python
from validators import validate_agent

config = {
    'slug': 'my-agent',
    'name': 'My Agent',
    'instructions': 'Detailed instructions for what this agent does...',
    'tools': ['Read', 'Grep']
}

is_valid, errors = validate_agent(config)
```

### Strict Validation (raises exceptions)

```python
from validators import validate_agent_strict, AgentValidationError

try:
    validate_agent_strict(config)
    print("Agent is valid!")
except AgentValidationError as e:
    print("Validation failed:")
    for error in e.errors:
        print(f"  - {error}")
```

### JSON Validation

```python
from validators import validate_agent_json

json_string = '{"slug": "test", "name": "Test", ...}'
is_valid, errors = validate_agent_json(json_string)
```

## Team Validation

### Basic Validation

```python
from validators import validate_team

team_config = {
    'slug': 'dev-team',
    'name': 'Development Team',
    'description': 'A team of agents working together',
    'agents': [
        {'slug': 'agent-1', 'role': 'developer'},
        {'slug': 'agent-2', 'role': 'reviewer'}
    ],
    'workflow': {
        'type': 'sequential'
    }
}

is_valid, errors = validate_team(team_config)
```

### Validation with Agent Existence Check

```python
from validators import validate_team

def check_agent_exists(slug):
    # Check your database or registry
    return slug in ['agent-1', 'agent-2', 'agent-3']

is_valid, errors = validate_team(team_config, agent_exists_fn=check_agent_exists)
```

## Validation Rules

### Agent Rules

**Required Fields:**
- `slug`: string, 3-100 chars, lowercase letters/numbers/hyphens only
- `name`: string, 2-255 chars
- `instructions`: string, 50-10000 chars
- `tools`: array of valid tool names

**Optional Fields:**
- `description`: string, max 1000 chars
- `category`: string, max 100 chars
- `skills`: array of strings
- `default_model`: 'sonnet' | 'haiku' | 'opus' (default: 'sonnet')
- `max_turns`: integer, 1-1000 (default: 50)
- `allowed_edit_patterns`: array of regex strings

**Valid Tools:**
- Read, Write, Edit, Glob, Grep, Bash, Task, TodoWrite

### Team Rules

**Required Fields:**
- `slug`: string, 3-100 chars, lowercase letters/numbers/hyphens only
- `name`: string, 2-255 chars
- `agents`: array of agent objects (min 1, max 50)

**Agent Object:**
- `slug`: required, must be valid agent slug
- `role`: recommended, string, max 100 chars
- `priority`: optional, integer 0-100

**Optional Fields:**
- `description`: string, max 1000 chars
- `orchestrator`: string (agent slug), must be in team
- `workflow`: object with workflow configuration
- `max_concurrent_tasks`: integer, 1-100
- `timeout`: positive number

**Valid Workflow Types:**
- sequential, parallel, orchestrated

**Additional Checks:**
- No duplicate agents in team
- All agent slugs must exist (if check function provided)
- Orchestrator must be part of the team
- Workflow stage agents must be in team

## Error Messages

All validation functions return helpful error messages:

```python
is_valid, errors = validate_agent({'slug': 'Bad_Slug!'})
# errors = [
#   "Missing required field: name",
#   "Missing required field: instructions",
#   "Missing required field: tools",
#   "Slug must contain only lowercase letters, numbers, and hyphens"
# ]
```

## Constants

```python
from validators import VALID_TOOLS, VALID_MODELS, VALID_WORKFLOW_TYPES, SLUG_PATTERN

print(VALID_TOOLS)
# ['Read', 'Write', 'Edit', 'Glob', 'Grep', 'Bash', 'Task', 'TodoWrite']

print(VALID_MODELS)
# ['sonnet', 'haiku', 'opus']

print(VALID_WORKFLOW_TYPES)
# ['sequential', 'parallel', 'orchestrated']

# Use SLUG_PATTERN for custom slug validation
import re
if SLUG_PATTERN.match('my-agent-123'):
    print("Valid slug!")
```

## Integration Example

```python
from validators import validate_agent_strict, AgentValidationError
import json

def create_agent_from_json(json_data):
    """Create agent after validation"""
    try:
        config = json.loads(json_data)
        validate_agent_strict(config)

        # Save to database
        agent_id = save_to_database(config)
        return agent_id

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    except AgentValidationError as e:
        raise ValueError(f"Invalid agent configuration: {', '.join(e.errors)}")
```

## Testing

Run the test suite:

```bash
python test_validators.py
```

The test suite covers:
- Import verification
- Valid agent configurations
- Invalid agent configurations
- Valid team configurations
- Invalid team configurations
- JSON validation
- Error message quality
