"""
Test script for agents, teams, and ratings API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_create_agent():
    """Test creating an agent"""
    print("\n=== Testing Agent Creation ===")

    agent_data = {
        "slug": "code-helper",
        "name": "Code Helper",
        "description": "A helpful coding assistant that can read, write, and edit files",
        "instructions": "You are a helpful coding assistant. You can read files, write new code, and make edits to existing code. Always explain your changes and follow best practices.",
        "tools": ["Read", "Write", "Edit", "Grep"],
        "skills": ["Python", "JavaScript", "Testing"],
        "default_model": "sonnet",
        "max_turns": 50,
        "metadata": {
            "author": "Test User",
            "version": "1.0.0"
        }
    }

    response = requests.post(f"{BASE_URL}/api/agents", json=agent_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json().get('id')

def test_get_agents():
    """Test listing all agents"""
    print("\n=== Testing Get All Agents ===")

    response = requests.get(f"{BASE_URL}/api/agents")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total agents: {data.get('total', 0)}")
    if data.get('agents'):
        print(f"First agent: {json.dumps(data['agents'][0], indent=2)}")

def test_get_agent(agent_id):
    """Test getting a specific agent"""
    print(f"\n=== Testing Get Agent {agent_id} ===")

    response = requests.get(f"{BASE_URL}/api/agents/{agent_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_rate_agent(agent_id):
    """Test rating an agent"""
    print(f"\n=== Testing Rate Agent {agent_id} ===")

    rating_data = {
        "rating": 5,
        "review": "Excellent agent! Very helpful for coding tasks."
    }

    response = requests.post(f"{BASE_URL}/api/agents/{agent_id}/rate", json=rating_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_download_agent(agent_id):
    """Test downloading an agent"""
    print(f"\n=== Testing Download Agent {agent_id} ===")

    response = requests.get(f"{BASE_URL}/api/agents/{agent_id}/download")
    print(f"Status: {response.status_code}")
    print(f"Response keys: {list(response.json().keys())}")

def test_create_team(agent_id):
    """Test creating a team"""
    print("\n=== Testing Team Creation ===")

    team_data = {
        "slug": "dev-team",
        "name": "Development Team",
        "description": "A team of agents for software development tasks",
        "version": "1.0.0",
        "agents": [
            {
                "slug": "code-helper",
                "role": "developer",
                "priority": 1
            }
        ],
        "workflow": {
            "type": "sequential",
            "stages": [
                {
                    "name": "Development",
                    "agents": ["code-helper"]
                }
            ]
        },
        "metadata": {
            "author": "Test User",
            "created_for": "Testing"
        }
    }

    response = requests.post(f"{BASE_URL}/api/teams", json=team_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json().get('id')

def test_get_teams():
    """Test listing all teams"""
    print("\n=== Testing Get All Teams ===")

    response = requests.get(f"{BASE_URL}/api/teams")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total teams: {data.get('total', 0)}")
    if data.get('teams'):
        print(f"First team: {json.dumps(data['teams'][0], indent=2)}")

def test_get_team(team_id):
    """Test getting a specific team"""
    print(f"\n=== Testing Get Team {team_id} ===")

    response = requests.get(f"{BASE_URL}/api/teams/{team_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_rate_team(team_id):
    """Test rating a team"""
    print(f"\n=== Testing Rate Team {team_id} ===")

    rating_data = {
        "rating": 4,
        "review": "Great team setup! Works well together."
    }

    response = requests.post(f"{BASE_URL}/api/teams/{team_id}/rate", json=rating_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_download_team(team_id):
    """Test downloading a team"""
    print(f"\n=== Testing Download Team {team_id} ===")

    response = requests.get(f"{BASE_URL}/api/teams/{team_id}/download")
    print(f"Status: {response.status_code}")
    print(f"Response keys: {list(response.json().keys())}")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Testing Agents, Teams, and Ratings API")
    print("=" * 60)

    try:
        # Test agents
        agent_id = test_create_agent()
        if agent_id:
            test_get_agents()
            test_get_agent(agent_id)
            test_rate_agent(agent_id)
            test_download_agent(agent_id)

            # Test teams
            team_id = test_create_team(agent_id)
            if team_id:
                test_get_teams()
                test_get_team(team_id)
                test_rate_team(team_id)
                test_download_team(team_id)

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
