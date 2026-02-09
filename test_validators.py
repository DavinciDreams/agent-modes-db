#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for validators module

This script verifies that:
1. Imports work correctly
2. Validation catches invalid configs
3. Validation passes valid configs
4. Error messages are helpful
"""

import sys
import json
import io

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def test_imports():
    """Test that all imports work correctly"""
    print("Testing imports...")
    try:
        from validators import (
            validate_agent, validate_team,
            AgentValidationError, TeamValidationError,
            VALID_TOOLS, VALID_MODELS, VALID_WORKFLOW_TYPES
        )
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_agent_validation():
    """Test agent validation"""
    print("\nTesting agent validation...")

    from validators import validate_agent, AgentValidationError, validate_agent_strict

    # Test valid agent
    valid_agent = {
        'slug': 'code-analyzer',
        'name': 'Code Analyzer',
        'instructions': 'You are a code analyzer that helps developers understand code structure and identify patterns. Your role is to analyze code and provide insights.',
        'tools': ['Read', 'Grep', 'Glob']
    }

    is_valid, errors = validate_agent(valid_agent)
    if is_valid:
        print("✓ Valid agent passed validation")
    else:
        print(f"✗ Valid agent failed: {errors}")
        return False

    # Test invalid agent - missing required fields
    invalid_agent_1 = {
        'slug': 'test'
    }

    is_valid, errors = validate_agent(invalid_agent_1)
    if not is_valid and len(errors) > 0:
        print(f"✓ Invalid agent (missing fields) correctly caught: {len(errors)} errors")
    else:
        print("✗ Invalid agent should have failed validation")
        return False

    # Test invalid agent - bad slug
    invalid_agent_2 = {
        'slug': 'Bad_Slug!',
        'name': 'Test',
        'instructions': 'Short instructions should fail minimum length validation here now',
        'tools': ['Read']
    }

    is_valid, errors = validate_agent(invalid_agent_2)
    if not is_valid:
        print(f"✓ Invalid agent (bad slug) correctly caught: {errors[0]}")
    else:
        print("✗ Invalid slug should have failed validation")
        return False

    # Test invalid agent - invalid tool
    invalid_agent_3 = {
        'slug': 'test-agent',
        'name': 'Test Agent',
        'instructions': 'This is a test agent with invalid tools that should fail validation',
        'tools': ['Read', 'InvalidTool']
    }

    is_valid, errors = validate_agent(invalid_agent_3)
    if not is_valid and any('InvalidTool' in e for e in errors):
        print("✓ Invalid agent (bad tool) correctly caught")
    else:
        print("✗ Invalid tool should have failed validation")
        return False

    # Test strict validation
    try:
        validate_agent_strict({'slug': 'test'})
        print("✗ Strict validation should have raised exception")
        return False
    except AgentValidationError as e:
        print(f"✓ Strict validation correctly raised exception with {len(e.errors)} errors")

    return True


def test_team_validation():
    """Test team validation"""
    print("\nTesting team validation...")

    from validators import validate_team, TeamValidationError, validate_team_strict

    # Mock agent exists function
    def agent_exists(slug):
        return slug in ['agent-1', 'agent-2', 'agent-3']

    # Test valid team
    valid_team = {
        'slug': 'dev-team',
        'name': 'Development Team',
        'description': 'A team of development agents',
        'agents': [
            {'slug': 'agent-1', 'role': 'developer'},
            {'slug': 'agent-2', 'role': 'reviewer'}
        ],
        'workflow': {
            'type': 'sequential'
        }
    }

    is_valid, errors = validate_team(valid_team, agent_exists)
    if is_valid:
        print("✓ Valid team passed validation")
    else:
        print(f"✗ Valid team failed: {errors}")
        return False

    # Test invalid team - missing required fields
    invalid_team_1 = {
        'slug': 'test'
    }

    is_valid, errors = validate_team(invalid_team_1)
    if not is_valid and len(errors) > 0:
        print(f"✓ Invalid team (missing fields) correctly caught: {len(errors)} errors")
    else:
        print("✗ Invalid team should have failed validation")
        return False

    # Test invalid team - duplicate agents
    invalid_team_2 = {
        'slug': 'dup-team',
        'name': 'Duplicate Team',
        'agents': [
            {'slug': 'agent-1', 'role': 'developer'},
            {'slug': 'agent-1', 'role': 'reviewer'}
        ]
    }

    is_valid, errors = validate_team(invalid_team_2, agent_exists)
    if not is_valid and any('Duplicate' in e for e in errors):
        print("✓ Invalid team (duplicate agents) correctly caught")
    else:
        print("✗ Duplicate agents should have failed validation")
        return False

    # Test invalid team - non-existent agent
    invalid_team_3 = {
        'slug': 'bad-team',
        'name': 'Bad Team',
        'agents': [
            {'slug': 'agent-1', 'role': 'developer'},
            {'slug': 'non-existent', 'role': 'reviewer'}
        ]
    }

    is_valid, errors = validate_team(invalid_team_3, agent_exists)
    if not is_valid and any('does not exist' in e for e in errors):
        print("✓ Invalid team (non-existent agent) correctly caught")
    else:
        print("✗ Non-existent agent should have failed validation")
        return False

    # Test invalid workflow type
    invalid_team_4 = {
        'slug': 'workflow-team',
        'name': 'Workflow Team',
        'agents': [
            {'slug': 'agent-1', 'role': 'developer'}
        ],
        'workflow': {
            'type': 'invalid-type'
        }
    }

    is_valid, errors = validate_team(invalid_team_4, agent_exists)
    if not is_valid and any('workflow type' in e.lower() for e in errors):
        print("✓ Invalid team (bad workflow type) correctly caught")
    else:
        print("✗ Invalid workflow type should have failed validation")
        return False

    # Test strict validation
    try:
        validate_team_strict({'slug': 'test'})
        print("✗ Strict validation should have raised exception")
        return False
    except TeamValidationError as e:
        print(f"✓ Strict validation correctly raised exception with {len(e.errors)} errors")

    return True


def test_json_validation():
    """Test JSON string validation"""
    print("\nTesting JSON validation...")

    from validators import validate_agent_json, validate_team_json

    # Test valid agent JSON
    valid_json = json.dumps({
        'slug': 'json-agent',
        'name': 'JSON Agent',
        'instructions': 'This is a test agent created from JSON to validate the JSON parsing functionality',
        'tools': ['Read']
    })

    is_valid, errors = validate_agent_json(valid_json)
    if is_valid:
        print("✓ Valid agent JSON passed validation")
    else:
        print(f"✗ Valid agent JSON failed: {errors}")
        return False

    # Test invalid JSON
    invalid_json = "{ invalid json }"

    is_valid, errors = validate_agent_json(invalid_json)
    if not is_valid and any('Invalid JSON' in e for e in errors):
        print("✓ Invalid JSON correctly caught")
    else:
        print("✗ Invalid JSON should have failed validation")
        return False

    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("VALIDATOR TEST SUITE")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Agent Validation", test_agent_validation),
        ("Team Validation", test_team_validation),
        ("JSON Validation", test_json_validation)
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
