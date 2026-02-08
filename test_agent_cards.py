"""
Test Agent Cards Functionality

This test file covers:
- Agent card generation from templates
- Agent card generation from configurations
- Agent card generation from custom agents
- Agent card validation
- Agent card export (JSON/YAML)
"""

import unittest
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from generators import AgentCardGenerator


class TestAgentCardGenerator(unittest.TestCase):
    """Test Agent Card Generator class"""
    
    def test_generate_from_template(self):
        """Test generating agent card from template"""
        template_data = {
            'id': 1,
            'name': 'Test Template',
            'description': 'A test template for agent cards',
            'category': 'Testing',
            'created_at': '2026-02-08T00:00:00Z',
            'updated_at': '2026-02-08T00:00:00Z'
        }
        
        card = AgentCardGenerator.generate_from_template(template_data)
        
        # Verify required fields
        self.assertEqual(card['$schema'], AgentCardGenerator.SCHEMA_URL)
        self.assertEqual(card['agent']['id'], 'template-1')
        self.assertEqual(card['agent']['name'], 'Test Template')
        self.assertEqual(card['agent']['description'], 'A test template for agent cards')
        self.assertEqual(card['agent']['category'], 'Testing')
        self.assertEqual(card['agent']['version'], '1.0.0')
        
        # Verify optional fields
        self.assertEqual(card['agent']['capabilities'], [])
        self.assertEqual(card['agent']['tools'], [])
        self.assertEqual(card['agent']['author']['name'], 'Agent Modes DB')
        self.assertIn('metadata', card['agent'])
        self.assertIn('compatibility', card['agent'])
    
    def test_generate_from_configuration(self):
        """Test generating agent card from configuration"""
        config_data = {
            'id': 1,
            'name': 'Test Configuration',
            'config_json': json.dumps({
                'capabilities': ['code_generation', 'testing'],
                'tools': ['python', 'pytest']
            }),
            'template_name': 'Test Template',
            'created_at': '2026-02-08T00:00:00Z',
            'updated_at': '2026-02-08T00:00:00Z'
        }
        
        card = AgentCardGenerator.generate_from_configuration(config_data)
        
        # Verify required fields
        self.assertEqual(card['$schema'], AgentCardGenerator.SCHEMA_URL)
        self.assertEqual(card['agent']['id'], 'configuration-1')
        self.assertEqual(card['agent']['name'], 'Test Configuration')
        self.assertEqual(card['agent']['category'], 'Configuration')
        
        # Verify capabilities and tools
        self.assertEqual(card['agent']['capabilities'], ['code_generation', 'testing'])
        self.assertEqual(card['agent']['tools'], ['python', 'pytest'])
    
    def test_generate_from_custom_agent(self):
        """Test generating agent card from custom agent"""
        agent_data = {
            'id': 1,
            'name': 'Test Agent',
            'description': 'A test custom agent',
            'capabilities': json.dumps(['code_review', 'debugging']),
            'tools': json.dumps(['git', 'docker']),
            'created_at': '2026-02-08T00:00:00Z',
            'updated_at': '2026-02-08T00:00:00Z'
        }
        
        card = AgentCardGenerator.generate_from_custom_agent(agent_data)
        
        # Verify required fields
        self.assertEqual(card['$schema'], AgentCardGenerator.SCHEMA_URL)
        self.assertEqual(card['agent']['id'], 'custom-agent-1')
        self.assertEqual(card['agent']['name'], 'Test Agent')
        self.assertEqual(card['agent']['category'], 'Custom')
        
        # Verify capabilities and tools
        self.assertEqual(card['agent']['capabilities'], ['code_review', 'debugging'])
        self.assertEqual(card['agent']['tools'], ['git', 'docker'])
    
    def test_generate_from_ir(self):
        """Test generating agent card from AgentIR"""
        agent_ir = {
            'id': 'ir-1',
            'name': 'IR Agent',
            'description': 'Agent from Intermediate Representation',
            'category': 'Development',
            'version': '2.0.0',
            'capabilities': ['analysis', 'generation'],
            'tools': ['code', 'docs'],
            'author': {
                'name': 'Test Author',
                'url': 'https://example.com'
            },
            'metadata': {
                'tags': ['dev', 'ai'],
                'language': 'en',
                'license': 'MIT'
            },
            'compatibility': {
                'platforms': ['web', 'desktop']
            }
        }
        
        card = AgentCardGenerator.generate_from_ir(agent_ir)
        
        # Verify all fields from IR
        self.assertEqual(card['agent']['id'], 'ir-1')
        self.assertEqual(card['agent']['name'], 'IR Agent')
        self.assertEqual(card['agent']['version'], '2.0.0')
        self.assertEqual(card['agent']['author']['name'], 'Test Author')
        self.assertEqual(card['agent']['compatibility']['platforms'], ['web', 'desktop'])
    
    def test_validate_card_valid(self):
        """Test validating a valid agent card"""
        card_data = {
            '$schema': AgentCardGenerator.SCHEMA_URL,
            'agent': {
                'id': 'test-1',
                'name': 'Test Agent',
                'description': 'A test agent',
                'version': '1.0.0',
                'category': 'Testing'
            }
        }
        
        is_valid, errors = AgentCardGenerator.validate_card(card_data)
        
        self.assertTrue(is_valid)
        self.assertIsNone(errors)
    
    def test_validate_card_missing_agent(self):
        """Test validating a card without agent key"""
        card_data = {
            '$schema': AgentCardGenerator.SCHEMA_URL
        }
        
        is_valid, errors = AgentCardGenerator.validate_card(card_data)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(errors)
        self.assertIn("Missing 'agent' key", errors[0])
    
    def test_validate_card_missing_required_fields(self):
        """Test validating a card with missing required fields"""
        card_data = {
            '$schema': AgentCardGenerator.SCHEMA_URL,
            'agent': {
                'id': 'test-1',
                'name': 'Test Agent'
            }
        }
        
        is_valid, errors = AgentCardGenerator.validate_card(card_data)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(errors)
        self.assertTrue(any('description' in e for e in errors))
        self.assertTrue(any('version' in e for e in errors))
        self.assertTrue(any('category' in e for e in errors))
    
    def test_export_card_json(self):
        """Test exporting agent card to JSON"""
        card_data = {
            '$schema': AgentCardGenerator.SCHEMA_URL,
            'agent': {
                'id': 'test-1',
                'name': 'Test Agent',
                'description': 'A test agent',
                'version': '1.0.0',
                'category': 'Testing'
            }
        }
        
        exported = AgentCardGenerator.export_card(card_data, 'json')
        
        # Verify it's valid JSON
        parsed = json.loads(exported)
        self.assertEqual(parsed['agent']['id'], 'test-1')
    
    def test_export_card_yaml(self):
        """Test exporting agent card to YAML"""
        card_data = {
            '$schema': AgentCardGenerator.SCHEMA_URL,
            'agent': {
                'id': 'test-1',
                'name': 'Test Agent',
                'description': 'A test agent',
                'version': '1.0.0',
                'category': 'Testing'
            }
        }
        
        exported = AgentCardGenerator.export_card(card_data, 'yaml')
        
        # Verify it's valid YAML (contains expected content)
        self.assertIn('agent:', exported)
        self.assertIn('name: Test Agent', exported)
    
    def test_export_card_invalid_format(self):
        """Test exporting with invalid format"""
        card_data = {
            '$schema': AgentCardGenerator.SCHEMA_URL,
            'agent': {
                'id': 'test-1',
                'name': 'Test Agent',
                'description': 'A test agent',
                'version': '1.0.0',
                'category': 'Testing'
            }
        }
        
        with self.assertRaises(ValueError) as context:
            AgentCardGenerator.export_card(card_data, 'invalid')
        
        self.assertIn('Unsupported export format', str(context.exception))
    
    def test_import_card_json(self):
        """Test importing agent card from JSON"""
        card_json = json.dumps({
            '$schema': AgentCardGenerator.SCHEMA_URL,
            'agent': {
                'id': 'test-1',
                'name': 'Test Agent',
                'description': 'A test agent',
                'version': '1.0.0',
                'category': 'Testing'
            }
        })
        
        card_data = AgentCardGenerator.import_card(card_json, 'json')
        
        self.assertEqual(card_data['agent']['id'], 'test-1')
        self.assertEqual(card_data['agent']['name'], 'Test Agent')
    
    def test_configuration_with_dict_config_json(self):
        """Test generating agent card from configuration with dict config_json"""
        config_data = {
            'id': 1,
            'name': 'Test Configuration',
            'config_json': {  # Dict instead of JSON string
                'capabilities': ['code_generation', 'testing'],
                'tools': ['python', 'pytest']
            },
            'template_name': 'Test Template',
            'created_at': '2026-02-08T00:00:00Z',
            'updated_at': '2026-02-08T00:00:00Z'
        }
        
        card = AgentCardGenerator.generate_from_configuration(config_data)
        
        # Verify capabilities and tools
        self.assertEqual(card['agent']['capabilities'], ['code_generation', 'testing'])
        self.assertEqual(card['agent']['tools'], ['python', 'pytest'])
    
    def test_custom_agent_with_list_capabilities(self):
        """Test generating agent card from custom agent with list capabilities"""
        agent_data = {
            'id': 1,
            'name': 'Test Agent',
            'description': 'A test custom agent',
            'capabilities': ['code_review', 'debugging'],  # List instead of JSON string
            'tools': ['git', 'docker'],  # List instead of JSON string
            'created_at': '2026-02-08T00:00:00Z',
            'updated_at': '2026-02-08T00:00:00Z'
        }
        
        card = AgentCardGenerator.generate_from_custom_agent(agent_data)
        
        # Verify capabilities and tools
        self.assertEqual(card['agent']['capabilities'], ['code_review', 'debugging'])
        self.assertEqual(card['agent']['tools'], ['git', 'docker'])


def run_tests():
    """Run all tests and print results"""
    print("\n" + "="*60)
    print("Agent Card Generator Tests")
    print("="*60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAgentCardGenerator)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
