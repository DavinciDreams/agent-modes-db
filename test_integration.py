#!/usr/bin/env python3
"""Integration tests for Agents and Teams API endpoints"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

# Use unique identifiers for this test run
TEST_SUFFIX = datetime.now().strftime("%Y%m%d%H%M%S")

def test_create_agent():
    """Test creating an agent via API"""
    print("\n=== TEST 1: Create Agent ===")

    agent_data = {
        "slug": f"test-agent-{TEST_SUFFIX}",
        "name": "Test Agent",
        "description": "A test agent for integration testing",
        "instructions": "You are a helpful test agent designed for integration testing. Your role is to assist with testing the agent management system by providing clear and accurate responses. Always be thorough in your testing approach.",
        "tools": ["Read", "Write", "Grep"],
        "skills": ["python", "testing"],
        "default_model": "sonnet",
        "max_turns": 30,
        "metadata": {
            "author": "Test Suite",
            "version": "1.0.0",
            "category": "testing"
        }
    }

    response = requests.post(f"{BASE_URL}/api/agents", json=agent_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    agent = response.json()
    assert agent["slug"] == f"test-agent-{TEST_SUFFIX}"
    assert agent["name"] == "Test Agent"

    return agent["id"]

def test_get_all_agents():
    """Test getting all agents"""
    print("\n=== TEST 2: Get All Agents ===")

    response = requests.get(f"{BASE_URL}/api/agents")
    print(f"Status: {response.status_code}")

    data = response.json()
    print(f"Found {len(data['agents'])} agents")

    assert response.status_code == 200
    assert len(data["agents"]) > 0

    return data["agents"]

def test_get_agent_by_id(agent_id):
    """Test getting a specific agent"""
    print(f"\n=== TEST 3: Get Agent by ID ({agent_id}) ===")

    response = requests.get(f"{BASE_URL}/api/agents/{agent_id}")
    print(f"Status: {response.status_code}")
    print(f"Agent: {response.json()['name']}")

    assert response.status_code == 200
    agent = response.json()
    assert agent["id"] == agent_id

    return agent

def test_rate_agent(agent_id):
    """Test rating an agent"""
    print(f"\n=== TEST 4: Rate Agent ({agent_id}) ===")

    rating_data = {
        "rating": 5,
        "review": "Excellent test agent! Very helpful."
    }

    response = requests.post(f"{BASE_URL}/api/agents/{agent_id}/rate", json=rating_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    data = response.json()
    assert "rating_average" in data

    # Verify the rating was applied
    agent = test_get_agent_by_id(agent_id)
    print(f"Agent rating average: {agent['rating_average']}")
    print(f"Agent rating count: {agent['rating_count']}")

    assert agent["rating_average"] == 5.0
    assert agent["rating_count"] == 1

def test_download_agent(agent_id):
    """Test downloading an agent in different formats"""
    print(f"\n=== TEST 5: Download Agent ({agent_id}) ===")

    # Test universal format (core functionality)
    response = requests.get(f"{BASE_URL}/api/agents/{agent_id}/download?format=universal")
    print(f"\nFormat: universal")
    print(f"Status: {response.status_code}")

    assert response.status_code == 200

    data = response.json()
    print(f"Universal format keys: {list(data.keys())[:5]}...")
    assert "name" in data
    assert "instructions" in data

    # Verify download count was incremented by fetching agent again
    agent = test_get_agent_by_id(agent_id)
    print(f"Download count after download: {agent['download_count']}")
    assert agent["download_count"] >= 1

    # TODO: Test claude and roo formats once converters are fully integrated

def test_create_team(agent_id):
    """Test creating a team with agents"""
    print(f"\n=== TEST 6: Create Team ===")

    team_data = {
        "slug": f"test-team-{TEST_SUFFIX}",
        "name": "Test Team",
        "description": "A test team for integration testing",
        "version": "1.0.0",
        "agents": [
            {
                "slug": f"test-agent-{TEST_SUFFIX}",
                "role": "Lead Developer"
            }
        ],
        "workflow": {
            "type": "sequential",
            "stages": [
                {
                    "name": "Development",
                    "agents": [f"test-agent-{TEST_SUFFIX}"]
                }
            ]
        },
        "metadata": {
            "author": "Test Suite",
            "version": "1.0.0"
        }
    }

    response = requests.post(f"{BASE_URL}/api/teams", json=team_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 201
    team = response.json()
    assert team["slug"] == f"test-team-{TEST_SUFFIX}"
    assert team["name"] == "Test Team"

    return team["id"]

def test_get_all_teams():
    """Test getting all teams"""
    print("\n=== TEST 7: Get All Teams ===")

    response = requests.get(f"{BASE_URL}/api/teams")
    print(f"Status: {response.status_code}")

    data = response.json()
    print(f"Found {len(data['teams'])} teams")

    assert response.status_code == 200
    assert len(data["teams"]) > 0

    return data["teams"]

def test_rate_team(team_id):
    """Test rating a team"""
    print(f"\n=== TEST 8: Rate Team ({team_id}) ===")

    rating_data = {
        "rating": 4,
        "review": "Great team setup!"
    }

    response = requests.post(f"{BASE_URL}/api/teams/{team_id}/rate", json=rating_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    data = response.json()
    assert "rating_average" in data

def run_all_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("AGENT MODES INTEGRATION TESTS")
    print("=" * 60)

    try:
        # Test Agents
        agent_id = test_create_agent()
        test_get_all_agents()
        test_get_agent_by_id(agent_id)
        test_rate_agent(agent_id)
        test_download_agent(agent_id)

        # Test Teams
        team_id = test_create_team(agent_id)
        test_get_all_teams()
        test_rate_team(team_id)

        print("\n" + "=" * 60)
        print("[PASS] ALL TESTS PASSED!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    # Give server a moment to be ready
    time.sleep(1)
    success = run_all_tests()
    exit(0 if success else 1)
