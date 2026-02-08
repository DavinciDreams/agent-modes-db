"""
Comprehensive API Testing for agent-modes-db

This test file covers:
- File Upload API endpoints
- Format Conversion API endpoints
- Template Creation from Upload API endpoints
- Agent Cards API endpoints
- Edge cases and error handling
"""

import unittest
import json
import os
import sys
import tempfile
import io

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Import Flask app
from app import app


class TestFileUploadAPI(unittest.TestCase):
    """Test File Upload API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_upload_file_json(self):
        """Test uploading a JSON file"""
        json_content = json.dumps({
            'name': 'Test Agent',
            'description': 'Test description',
            'capabilities': ['test'],
            'tools': ['test-tool'],
            'system_prompt': 'Test prompt'
        })
        
        data = {
            'file': (io.BytesIO(json_content.encode('utf-8')), 'test_agent.json')
        }
        
        response = self.app.post('/api/files/upload', 
                                 content_type='multipart/form-data',
                                 data=data)
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertIn('upload_id', response_data)
        self.assertEqual(response_data['file_format'], 'json')
        self.assertEqual(response_data['upload_status'], 'completed')
    
    def test_upload_file_yaml(self):
        """Test uploading a YAML file"""
        yaml_content = """
name: Test Agent
description: Test description
capabilities:
  - test
tools:
  - test-tool
system_prompt: Test prompt
"""
        
        data = {
            'file': (io.BytesIO(yaml_content.encode('utf-8')), 'test_agent.yaml')
        }
        
        response = self.app.post('/api/files/upload', 
                                 content_type='multipart/form-data',
                                 data=data)
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertIn('upload_id', response_data)
        self.assertEqual(response_data['file_format'], 'yaml')
    
    def test_upload_file_invalid_format(self):
        """Test uploading an invalid file format"""
        data = {
            'file': (io.BytesIO(b'test content'), 'test.txt')
        }
        
        response = self.app.post('/api/files/upload', 
                                 content_type='multipart/form-data',
                                 data=data)
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('Invalid file format', response_data['error'])
    
    def test_upload_file_no_file(self):
        """Test upload without providing a file"""
        response = self.app.post('/api/files/upload', 
                                 content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('No file provided', response_data['error'])
    
    def test_upload_multiple_files(self):
        """Test uploading multiple files"""
        json_content = json.dumps({
            'name': 'Test Agent 1',
            'description': 'Test description 1',
            'capabilities': ['test1'],
            'tools': ['test-tool1'],
            'system_prompt': 'Test prompt 1'
        })
        
        yaml_content = """
name: Test Agent 2
description: Test description 2
capabilities:
  - test2
tools:
  - test-tool2
system_prompt: Test prompt 2
"""
        
        data = {
            'files': [
                (io.BytesIO(json_content.encode('utf-8')), 'test_agent1.json'),
                (io.BytesIO(yaml_content.encode('utf-8')), 'test_agent2.yaml')
            ]
        }
        
        response = self.app.post('/api/files/upload/multiple', 
                                 content_type='multipart/form-data',
                                 data=data)
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertIn('uploads', response_data)
        self.assertEqual(response_data['total'], 2)
        self.assertEqual(response_data['successful'], 2)
        self.assertEqual(response_data['failed'], 0)
    
    def test_get_file_uploads(self):
        """Test getting all file uploads"""
        # First upload a file
        json_content = json.dumps({
            'name': 'Test Agent',
            'description': 'Test description',
            'capabilities': ['test'],
            'tools': ['test-tool'],
            'system_prompt': 'Test prompt'
        })
        
        data = {
            'file': (io.BytesIO(json_content.encode('utf-8')), 'test_agent.json')
        }
        
        self.app.post('/api/files/upload', 
                      content_type='multipart/form-data',
                      data=data)
        
        # Get all uploads
        response = self.app.get('/api/files')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('uploads', response_data)
        self.assertIn('total', response_data)
        self.assertGreater(response_data['total'], 0)
    
    def test_get_file_upload_by_id(self):
        """Test getting a specific file upload by ID"""
        # First upload a file
        json_content = json.dumps({
            'name': 'Test Agent',
            'description': 'Test description',
            'capabilities': ['test'],
            'tools': ['test-tool'],
            'system_prompt': 'Test prompt'
        })
        
        data = {
            'file': (io.BytesIO(json_content.encode('utf-8')), 'test_agent.json')
        }
        
        upload_response = self.app.post('/api/files/upload', 
                                        content_type='multipart/form-data',
                                        data=data)
        
        upload_data = json.loads(upload_response.data)
        upload_id = upload_data['upload_id']
        
        # Get upload by ID
        response = self.app.get(f'/api/files/{upload_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['upload_id'], upload_id)
    
    def test_get_file_upload_not_found(self):
        """Test getting a non-existent file upload"""
        response = self.app.get('/api/files/99999')
        
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('not found', response_data['error'].lower())
    
    def test_delete_file_upload(self):
        """Test deleting a file upload"""
        # First upload a file
        json_content = json.dumps({
            'name': 'Test Agent',
            'description': 'Test description',
            'capabilities': ['test'],
            'tools': ['test-tool'],
            'system_prompt': 'Test prompt'
        })
        
        data = {
            'file': (io.BytesIO(json_content.encode('utf-8')), 'test_agent.json')
        }
        
        upload_response = self.app.post('/api/files/upload', 
                                        content_type='multipart/form-data',
                                        data=data)
        
        upload_data = json.loads(upload_response.data)
        upload_id = upload_data['upload_id']
        
        # Delete upload
        response = self.app.delete(f'/api/files/{upload_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('message', response_data)
        self.assertIn('deleted successfully', response_data['message'])


class TestFormatConversionAPI(unittest.TestCase):
    """Test Format Conversion API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_convert_claude_to_roo(self):
        """Test converting from Claude to Roo format"""
        data = {
            'source_format': 'claude',
            'target_format': 'roo',
            'agent_data': {
                'name': 'Test Agent',
                'description': 'Test description',
                'capabilities': ['test'],
                'tools': ['test-tool'],
                'system_prompt': 'Test prompt'
            }
        }
        
        response = self.app.post('/api/convert',
                                 content_type='application/json',
                                 data=json.dumps(data))
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('conversion_id', response_data)
        self.assertEqual(response_data['source_format'], 'claude')
        self.assertEqual(response_data['target_format'], 'roo')
        self.assertIn('target_data', response_data)
        self.assertIn('mode', response_data['target_data'])
    
    def test_convert_roo_to_claude(self):
        """Test converting from Roo to Claude format"""
        data = {
            'source_format': 'roo',
            'target_format': 'claude',
            'agent_data': {
                'mode': 'test-mode',
                'name': 'Test Agent',
                'description': 'Test description',
                'capabilities': ['test'],
                'tools': ['test-tool'],
                'system_prompt': 'Test prompt'
            }
        }
        
        response = self.app.post('/api/convert',
                                 content_type='application/json',
                                 data=json.dumps(data))
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['source_format'], 'roo')
        self.assertEqual(response_data['target_format'], 'claude')
        self.assertIn('target_data', response_data)
        self.assertNotIn('mode', response_data['target_data'])
    
    def test_convert_missing_fields(self):
        """Test conversion with missing required fields"""
        data = {
            'source_format': 'claude',
            'target_format': 'roo'
        }
        
        response = self.app.post('/api/convert',
                                 content_type='application/json',
                                 data=json.dumps(data))
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('Missing required fields', response_data['error'])
    
    def test_convert_invalid_format(self):
        """Test conversion with invalid format"""
        data = {
            'source_format': 'invalid',
            'target_format': 'roo',
            'agent_data': {}
        }
        
        response = self.app.post('/api/convert',
                                 content_type='application/json',
                                 data=json.dumps(data))
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    def test_convert_same_format(self):
        """Test conversion to same format (should fail)"""
        data = {
            'source_format': 'claude',
            'target_format': 'claude',
            'agent_data': {
                'name': 'Test Agent',
                'description': 'Test description',
                'capabilities': ['test'],
                'tools': ['test-tool'],
                'system_prompt': 'Test prompt'
            }
        }
        
        response = self.app.post('/api/convert',
                                 content_type='application/json',
                                 data=json.dumps(data))
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    def test_get_conversion_history(self):
        """Test getting conversion history"""
        # First perform a conversion
        data = {
            'source_format': 'claude',
            'target_format': 'roo',
            'agent_data': {
                'name': 'Test Agent',
                'description': 'Test description',
                'capabilities': ['test'],
                'tools': ['test-tool'],
                'system_prompt': 'Test prompt'
            }
        }
        
        self.app.post('/api/convert',
                      content_type='application/json',
                      data=json.dumps(data))
        
        # Get conversion history
        response = self.app.get('/api/convert/history')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('conversions', response_data)
        self.assertIn('total', response_data)
    
    def test_get_supported_formats(self):
        """Test getting supported formats"""
        response = self.app.get('/api/convert/formats')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('formats', response_data)
        self.assertIn('claude', response_data['formats'])
        self.assertIn('roo', response_data['formats'])
        self.assertIn('custom', response_data['formats'])


class TestTemplateCreationAPI(unittest.TestCase):
    """Test Template Creation from Upload API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_create_template_from_upload(self):
        """Test creating a template from an uploaded file"""
        # First upload a file
        json_content = json.dumps({
            'name': 'Test Agent',
            'description': 'Test description',
            'capabilities': ['test'],
            'tools': ['test-tool'],
            'system_prompt': 'Test prompt'
        })
        
        upload_data = {
            'file': (io.BytesIO(json_content.encode('utf-8')), 'test_agent.json')
        }
        
        upload_response = self.app.post('/api/files/upload',
                                       content_type='multipart/form-data',
                                       data=upload_data)
        
        upload_result = json.loads(upload_response.data)
        upload_id = upload_result['upload_id']
        
        # Create template from upload
        template_data = {
            'upload_id': upload_id,
            'name': 'Test Template',
            'description': 'Template from upload',
            'category': 'Testing'
        }
        
        response = self.app.post('/api/templates/from-upload',
                                 content_type='application/json',
                                 data=json.dumps(template_data))
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertIn('id', response_data)
        self.assertEqual(response_data['name'], 'Test Template')
        self.assertEqual(response_data['is_imported'], True)
    
    def test_create_template_from_data(self):
        """Test creating a template from parsed data"""
        template_data = {
            'source_format': 'claude',
            'agent_data': {
                'name': 'Test Agent',
                'description': 'Test description',
                'capabilities': ['test'],
                'tools': ['test-tool'],
                'system_prompt': 'Test prompt'
            },
            'name': 'Test Template',
            'description': 'Template from data',
            'category': 'Testing'
        }
        
        response = self.app.post('/api/templates/from-data',
                                 content_type='application/json',
                                 data=json.dumps(template_data))
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertIn('id', response_data)
        self.assertEqual(response_data['name'], 'Test Template')
        self.assertEqual(response_data['is_imported'], True)
    
    def test_create_template_from_upload_missing_fields(self):
        """Test creating template from upload with missing fields"""
        template_data = {
            'upload_id': 1,
            'name': 'Test Template'
        }
        
        response = self.app.post('/api/templates/from-upload',
                                 content_type='application/json',
                                 data=json.dumps(template_data))
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('Missing required fields', response_data['error'])


class TestAgentCardsAPI(unittest.TestCase):
    """Test Agent Cards API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_get_all_agent_cards(self):
        """Test getting all agent cards"""
        response = self.app.get('/api/agent-cards')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('cards', response_data)
        self.assertIn('total', response_data)
    
    def test_get_agent_cards_with_filter(self):
        """Test getting agent cards with entity type filter"""
        response = self.app.get('/api/agent-cards?entity_type=template')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('cards', response_data)
    
    def test_generate_agent_card_from_template(self):
        """Test generating agent card from template"""
        # First create a template
        template_data = {
            'name': 'Test Template',
            'description': 'Test description',
            'category': 'Testing'
        }
        
        template_response = self.app.post('/api/templates',
                                          content_type='application/json',
                                          data=json.dumps(template_data))
        
        template_result = json.loads(template_response.data)
        template_id = template_result['id']
        
        # Generate agent card
        card_data = {
            'entity_type': 'template',
            'entity_id': template_id
        }
        
        print(f"TEST DEBUG: Calling generate endpoint for entity_id={template_id}")
        response = self.app.post('/api/agent-cards/generate',
                                 content_type='application/json',
                                 data=json.dumps(card_data))
        
        print(f"TEST DEBUG: Response status code = {response.status_code}")
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertIn('id', response_data)
        self.assertIn('card', response_data)
    
    def test_generate_agent_card_missing_fields(self):
        """Test generating agent card with missing fields"""
        card_data = {
            'entity_type': 'template'
        }
        
        response = self.app.post('/api/agent-cards/generate',
                                 content_type='application/json',
                                 data=json.dumps(card_data))
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('Missing required fields', response_data['error'])
    
    def test_generate_agent_card_invalid_entity_type(self):
        """Test generating agent card with invalid entity type"""
        card_data = {
            'entity_type': 'invalid',
            'entity_id': 1
        }
        
        response = self.app.post('/api/agent-cards/generate',
                                 content_type='application/json',
                                 data=json.dumps(card_data))
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('Invalid entity type', response_data['error'])
    
    def test_generate_agent_cards_batch(self):
        """Test generating multiple agent cards"""
        # First create templates
        template_data = {
            'name': 'Test Template',
            'description': 'Test description',
            'category': 'Testing'
        }
        
        template_response1 = self.app.post('/api/templates',
                                           content_type='application/json',
                                           data=json.dumps(template_data))
        
        template_response2 = self.app.post('/api/templates',
                                           content_type='application/json',
                                           data=json.dumps({
                                               'name': 'Test Template 2',
                                               'description': 'Test description 2',
                                               'category': 'Testing'
                                           }))
        
        template_result1 = json.loads(template_response1.data)
        template_result2 = json.loads(template_response2.data)
        
        # Generate agent cards batch
        card_data = {
            'entities': [
                {'entity_type': 'template', 'entity_id': template_result1['id']},
                {'entity_type': 'template', 'entity_id': template_result2['id']}
            ]
        }
        
        response = self.app.post('/api/agent-cards/generate/batch',
                                 content_type='application/json',
                                 data=json.dumps(card_data))
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('results', response_data)
        self.assertEqual(response_data['total'], 2)
        self.assertEqual(response_data['successful'], 2)
        self.assertEqual(response_data['failed'], 0)
    
    def test_export_agent_card_json(self):
        """Test exporting agent card as JSON"""
        # First create a template and generate card
        template_data = {
            'name': 'Test Template',
            'description': 'Test description',
            'category': 'Testing'
        }
        
        template_response = self.app.post('/api/templates',
                                          content_type='application/json',
                                          data=json.dumps(template_data))
        
        template_result = json.loads(template_response.data)
        
        card_data = {
            'entity_type': 'template',
            'entity_id': template_result['id']
        }
        
        card_response = self.app.post('/api/agent-cards/generate',
                                      content_type='application/json',
                                      data=json.dumps(card_data))
        
        card_result = json.loads(card_response.data)
        card_id = card_result['id']
        
        # Export card
        response = self.app.get(f'/api/agent-cards/{card_id}/export?format=json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['format'], 'json')
        self.assertIn('content', response_data)
        self.assertIn('filename', response_data)
    
    def test_export_agent_card_yaml(self):
        """Test exporting agent card as YAML"""
        # First create a template and generate card
        template_data = {
            'name': 'Test Template',
            'description': 'Test description',
            'category': 'Testing'
        }
        
        template_response = self.app.post('/api/templates',
                                          content_type='application/json',
                                          data=json.dumps(template_data))
        
        template_result = json.loads(template_response.data)
        
        card_data = {
            'entity_type': 'template',
            'entity_id': template_result['id']
        }
        
        card_response = self.app.post('/api/agent-cards/generate',
                                      content_type='application/json',
                                      data=json.dumps(card_data))
        
        card_result = json.loads(card_response.data)
        card_id = card_result['id']
        
        # Export card
        response = self.app.get(f'/api/agent-cards/{card_id}/export?format=yaml')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['format'], 'yaml')
        self.assertIn('content', response_data)
    
    def test_export_agent_card_invalid_format(self):
        """Test exporting agent card with invalid format"""
        response = self.app.get('/api/agent-cards/1/export?format=invalid')
        
        self.assertEqual(response.status_code, 404)  # Card doesn't exist yet
    
    def test_validate_agent_card(self):
        """Test validating an agent card"""
        # First create a template and generate card
        template_data = {
            'name': 'Test Template',
            'description': 'Test description',
            'category': 'Testing'
        }
        
        template_response = self.app.post('/api/templates',
                                          content_type='application/json',
                                          data=json.dumps(template_data))
        
        template_result = json.loads(template_response.data)
        
        card_data = {
            'entity_type': 'template',
            'entity_id': template_result['id']
        }
        
        card_response = self.app.post('/api/agent-cards/generate',
                                      content_type='application/json',
                                      data=json.dumps(card_data))
        
        card_result = json.loads(card_response.data)
        card_id = card_result['id']
        
        # Validate card
        response = self.app.post(f'/api/agent-cards/{card_id}/validate')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('valid', response_data)
        self.assertTrue(response_data['valid'])


class TestRegressionAPI(unittest.TestCase):
    """Test existing functionality still works (regression testing)"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_get_templates(self):
        """Test getting all templates (existing functionality)"""
        response = self.app.get('/api/templates')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
    
    def test_create_template(self):
        """Test creating a template (existing functionality)"""
        template_data = {
            'name': 'Test Template',
            'description': 'Test description',
            'category': 'Testing'
        }
        
        response = self.app.post('/api/templates',
                                 content_type='application/json',
                                 data=json.dumps(template_data))
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertIn('id', response_data)
    
    def test_update_template(self):
        """Test updating a template (existing functionality)"""
        # First create a template
        template_data = {
            'name': 'Test Template',
            'description': 'Test description',
            'category': 'Testing'
        }
        
        create_response = self.app.post('/api/templates',
                                        content_type='application/json',
                                        data=json.dumps(template_data))
        
        create_result = json.loads(create_response.data)
        template_id = create_result['id']
        
        # Update template
        update_data = {
            'name': 'Updated Template',
            'description': 'Updated description',
            'category': 'Updated'
        }
        
        response = self.app.put(f'/api/templates/{template_id}',
                                content_type='application/json',
                                data=json.dumps(update_data))
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('message', response_data)
    
    def test_delete_template(self):
        """Test deleting a template (existing functionality)"""
        # First create a template
        template_data = {
            'name': 'Test Template',
            'description': 'Test description',
            'category': 'Testing'
        }
        
        create_response = self.app.post('/api/templates',
                                        content_type='application/json',
                                        data=json.dumps(template_data))
        
        create_result = json.loads(create_response.data)
        template_id = create_result['id']
        
        # Delete template
        response = self.app.delete(f'/api/templates/{template_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('message', response_data)
    
    def test_protect_builtin_template(self):
        """Test that builtin templates are protected"""
        # Get a builtin template
        templates_response = self.app.get('/api/templates')
        templates = json.loads(templates_response.data)
        
        # Find a builtin template
        builtin_template = None
        for template in templates:
            if template.get('is_builtin'):
                builtin_template = template
                break
        
        if builtin_template:
            # Try to update builtin template
            update_data = {
                'name': 'Hacked Template',
                'description': 'Hacked description',
                'category': 'Hacked'
            }
            
            response = self.app.put(f"/api/templates/{builtin_template['id']}",
                                    content_type='application/json',
                                    data=json.dumps(update_data))
            
            self.assertEqual(response.status_code, 403)
            response_data = json.loads(response.data)
            self.assertIn('error', response_data)
            self.assertIn('builtin', response_data['error'].lower())


def run_tests():
    """Run all API tests and print results"""
    print("\n" + "="*60)
    print("COMPREHENSIVE API TESTS")
    print("="*60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFileUploadAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestFormatConversionAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestTemplateCreationAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentCardsAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestRegressionAPI))
    
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
