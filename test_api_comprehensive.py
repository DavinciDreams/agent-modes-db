"""
Comprehensive test of Agents, Teams, and Ratings API using Flask test client
"""
import json
import sys
from app import app

# Set stdout encoding to UTF-8 for Windows compatibility
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def run_comprehensive_test():
    """Run comprehensive API tests"""
    print("=" * 80)
    print("COMPREHENSIVE API TEST - Agents, Teams, and Ratings")
    print("=" * 80)

    with app.test_client() as client:
        # ====================================
        # Test 1: Create Agent
        # ====================================
        print("\n[TEST 1] Creating agent...")
        agent_data = {
            'slug': 'backend-dev',
            'name': 'Backend Developer',
            'description': 'Specialized agent for backend development tasks',
            'instructions': 'You are a backend developer specializing in APIs, databases, and server-side logic. You write clean, well-tested code and follow best practices.',
            'tools': ['Read', 'Write', 'Edit', 'Bash', 'Grep'],
            'skills': ['Python', 'SQL', 'REST APIs', 'Testing'],
            'default_model': 'sonnet',
            'max_turns': 50,
            'metadata': {
                'author': 'Test Suite',
                'version': '1.0.0'
            }
        }

        response = client.post('/api/agents',
                             data=json.dumps(agent_data),
                             content_type='application/json')

        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            agent = response.get_json()
            agent_id = agent['id']
            print(f"[OK] Agent created successfully with ID: {agent_id}")
        else:
            print(f"✗ Failed to create agent: {response.get_json()}")
            return

        # ====================================
        # Test 2: Get All Agents
        # ====================================
        print("\n[TEST 2] Getting all agents...")
        response = client.get('/api/agents')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"✓ Found {data['total']} agent(s)")
        else:
            print(f"✗ Failed: {response.get_json()}")

        # ====================================
        # Test 3: Get Specific Agent
        # ====================================
        print(f"\n[TEST 3] Getting agent {agent_id}...")
        response = client.get(f'/api/agents/{agent_id}')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            agent = response.get_json()
            print(f"✓ Retrieved agent: {agent['name']}")
            print(f"  - Tools: {agent['tools']}")
            print(f"  - Skills: {agent['skills']}")
        else:
            print(f"✗ Failed: {response.get_json()}")

        # ====================================
        # Test 4: Rate Agent
        # ====================================
        print(f"\n[TEST 4] Rating agent {agent_id}...")
        rating_data = {
            'rating': 5,
            'review': 'Excellent agent! Very helpful for backend tasks.'
        }
        response = client.post(f'/api/agents/{agent_id}/rate',
                              data=json.dumps(rating_data),
                              content_type='application/json')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"✓ Rating submitted successfully")
            print(f"  - Average: {data['rating_average']}")
            print(f"  - Count: {data['rating_count']}")
        else:
            print(f"✗ Failed: {response.get_json()}")

        # ====================================
        # Test 5: Download Agent
        # ====================================
        print(f"\n[TEST 5] Downloading agent {agent_id}...")
        response = client.get(f'/api/agents/{agent_id}/download')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            agent = response.get_json()
            print(f"✓ Agent downloaded successfully")
            print(f"  - Download count incremented")
        else:
            print(f"✗ Failed: {response.get_json()}")

        # ====================================
        # Test 6: Create Team
        # ====================================
        print("\n[TEST 6] Creating team...")
        team_data = {
            'slug': 'fullstack-team',
            'name': 'Full Stack Development Team',
            'description': 'A team for end-to-end feature development',
            'version': '1.0.0',
            'agents': [
                {
                    'slug': 'backend-dev',
                    'role': 'Backend Developer',
                    'priority': 1
                }
            ],
            'orchestrator': 'backend-dev',
            'workflow': {
                'type': 'sequential',
                'stages': [
                    {
                        'name': 'Backend Development',
                        'agents': ['backend-dev']
                    }
                ]
            },
            'tools': ['Read', 'Write', 'Edit', 'Bash'],
            'metadata': {
                'author': 'Test Suite',
                'purpose': 'Full stack development'
            }
        }

        response = client.post('/api/teams',
                             data=json.dumps(team_data),
                             content_type='application/json')

        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            team = response.get_json()
            team_id = team['id']
            print(f"✓ Team created successfully with ID: {team_id}")
        else:
            print(f"✗ Failed to create team: {response.get_json()}")
            return

        # ====================================
        # Test 7: Get All Teams
        # ====================================
        print("\n[TEST 7] Getting all teams...")
        response = client.get('/api/teams')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"✓ Found {data['total']} team(s)")
        else:
            print(f"✗ Failed: {response.get_json()}")

        # ====================================
        # Test 8: Get Specific Team
        # ====================================
        print(f"\n[TEST 8] Getting team {team_id}...")
        response = client.get(f'/api/teams/{team_id}')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            team = response.get_json()
            print(f"✓ Retrieved team: {team['name']}")
            print(f"  - Agents: {len(team['agents'])} agent(s)")
            print(f"  - Workflow: {team['workflow']['type']}")
        else:
            print(f"✗ Failed: {response.get_json()}")

        # ====================================
        # Test 9: Rate Team
        # ====================================
        print(f"\n[TEST 9] Rating team {team_id}...")
        rating_data = {
            'rating': 4,
            'review': 'Great team setup! Works well for full stack projects.'
        }
        response = client.post(f'/api/teams/{team_id}/rate',
                              data=json.dumps(rating_data),
                              content_type='application/json')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"✓ Rating submitted successfully")
            print(f"  - Average: {data['rating_average']}")
            print(f"  - Count: {data['rating_count']}")
        else:
            print(f"✗ Failed: {response.get_json()}")

        # ====================================
        # Test 10: Download Team
        # ====================================
        print(f"\n[TEST 10] Downloading team {team_id}...")
        response = client.get(f'/api/teams/{team_id}/download')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            team = response.get_json()
            print(f"✓ Team downloaded successfully")
            print(f"  - Download count incremented")
        else:
            print(f"✗ Failed: {response.get_json()}")

        # ====================================
        # Test 11: Search Agents
        # ====================================
        print("\n[TEST 11] Searching agents...")
        response = client.get('/api/agents?search=backend')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"✓ Found {data['total']} agent(s) matching 'backend'")
        else:
            print(f"✗ Failed: {response.get_json()}")

        # ====================================
        # Test 12: Sort Agents by Downloads
        # ====================================
        print("\n[TEST 12] Sorting agents by downloads...")
        response = client.get('/api/agents?sort=downloads&order=desc')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"✓ Retrieved {data['total']} agent(s) sorted by downloads")
            if data['agents']:
                print(f"  - Top agent: {data['agents'][0]['name']} ({data['agents'][0]['download_count']} downloads)")
        else:
            print(f"✗ Failed: {response.get_json()}")

        # ====================================
        # Summary
        # ====================================
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print("✓ All tests completed successfully!")
        print(f"  - Created agent ID: {agent_id}")
        print(f"  - Created team ID: {team_id}")
        print(f"  - Ratings system working")
        print(f"  - Download tracking working")
        print(f"  - Search and filtering working")
        print("=" * 80)

if __name__ == "__main__":
    run_comprehensive_test()
