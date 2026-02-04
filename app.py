from flask import Flask, request, jsonify, render_template
import database as db
import json
import os

app = Flask(__name__)

# Initialize database on first run
if not os.path.exists('agents.db'):
    db.init_db()
    print("Database initialized with seed data")

# Serve the main page
@app.route('/')
def index():
    return render_template('index.html')

# API Error handler
@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({'error': str(e)}), 400

# ============================================
# Agent Templates API
# ============================================

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all templates"""
    templates = db.get_all_templates()
    return jsonify(templates)

@app.route('/api/templates/<int:template_id>', methods=['GET'])
def get_template(template_id):
    """Get specific template"""
    template = db.get_template_by_id(template_id)
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    return jsonify(template)

@app.route('/api/templates', methods=['POST'])
def create_template():
    """Create new template"""
    data = request.get_json()

    if not all(k in data for k in ['name', 'description', 'category']):
        return jsonify({'error': 'Missing required fields'}), 400

    template_id = db.create_template(
        name=data['name'],
        description=data['description'],
        category=data['category'],
        is_builtin=data.get('is_builtin', False)
    )

    return jsonify({'id': template_id, 'message': 'Template created successfully'}), 201

@app.route('/api/templates/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """Update existing template"""
    data = request.get_json()

    if not all(k in data for k in ['name', 'description', 'category']):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if template exists
    template = db.get_template_by_id(template_id)
    if not template:
        return jsonify({'error': 'Template not found'}), 404

    # Prevent updating builtin templates
    if template['is_builtin']:
        return jsonify({'error': 'Cannot update builtin templates'}), 403

    db.update_template(
        template_id=template_id,
        name=data['name'],
        description=data['description'],
        category=data['category']
    )

    return jsonify({'message': 'Template updated successfully'})

@app.route('/api/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete template"""
    try:
        db.delete_template(template_id)
        return jsonify({'message': 'Template deleted successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================
# Agent Configurations API
# ============================================

@app.route('/api/configurations', methods=['GET'])
def get_configurations():
    """Get all configurations"""
    configurations = db.get_all_configurations()
    return jsonify(configurations)

@app.route('/api/configurations/<int:config_id>', methods=['GET'])
def get_configuration(config_id):
    """Get specific configuration"""
    configuration = db.get_configuration_by_id(config_id)
    if not configuration:
        return jsonify({'error': 'Configuration not found'}), 404
    return jsonify(configuration)

@app.route('/api/configurations', methods=['POST'])
def create_configuration():
    """Create new configuration"""
    data = request.get_json()

    if not all(k in data for k in ['name', 'config_json']):
        return jsonify({'error': 'Missing required fields'}), 400

    # Validate JSON
    config_json = data['config_json']
    if isinstance(config_json, str):
        try:
            config_json = json.loads(config_json)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON in config_json'}), 400

    config_id = db.create_configuration(
        name=data['name'],
        template_id=data.get('template_id'),
        config_json=config_json
    )

    return jsonify({'id': config_id, 'message': 'Configuration created successfully'}), 201

@app.route('/api/configurations/<int:config_id>', methods=['PUT'])
def update_configuration(config_id):
    """Update existing configuration"""
    data = request.get_json()

    if not all(k in data for k in ['name', 'config_json']):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if configuration exists
    configuration = db.get_configuration_by_id(config_id)
    if not configuration:
        return jsonify({'error': 'Configuration not found'}), 404

    # Validate JSON
    config_json = data['config_json']
    if isinstance(config_json, str):
        try:
            config_json = json.loads(config_json)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON in config_json'}), 400

    db.update_configuration(
        config_id=config_id,
        name=data['name'],
        template_id=data.get('template_id'),
        config_json=config_json
    )

    return jsonify({'message': 'Configuration updated successfully'})

@app.route('/api/configurations/<int:config_id>', methods=['DELETE'])
def delete_configuration(config_id):
    """Delete configuration"""
    db.delete_configuration(config_id)
    return jsonify({'message': 'Configuration deleted successfully'})

# ============================================
# Custom Agents API
# ============================================

@app.route('/api/custom-agents', methods=['GET'])
def get_custom_agents():
    """Get all custom agents"""
    agents = db.get_all_custom_agents()
    return jsonify(agents)

@app.route('/api/custom-agents/<int:agent_id>', methods=['GET'])
def get_custom_agent(agent_id):
    """Get specific custom agent"""
    agent = db.get_custom_agent_by_id(agent_id)
    if not agent:
        return jsonify({'error': 'Custom agent not found'}), 404
    return jsonify(agent)

@app.route('/api/custom-agents', methods=['POST'])
def create_custom_agent():
    """Create new custom agent"""
    data = request.get_json()

    required_fields = ['name', 'description', 'capabilities', 'tools', 'system_prompt']
    if not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Parse capabilities and tools
    capabilities = data['capabilities']
    if isinstance(capabilities, str):
        try:
            capabilities = json.loads(capabilities)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON in capabilities'}), 400

    tools = data['tools']
    if isinstance(tools, str):
        try:
            tools = json.loads(tools)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON in tools'}), 400

    # Parse config_schema if provided
    config_schema = data.get('config_schema')
    if config_schema and isinstance(config_schema, str):
        try:
            config_schema = json.loads(config_schema)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON in config_schema'}), 400

    agent_id = db.create_custom_agent(
        name=data['name'],
        description=data['description'],
        capabilities=capabilities,
        tools=tools,
        system_prompt=data['system_prompt'],
        config_schema=config_schema
    )

    return jsonify({'id': agent_id, 'message': 'Custom agent created successfully'}), 201

@app.route('/api/custom-agents/<int:agent_id>', methods=['PUT'])
def update_custom_agent(agent_id):
    """Update existing custom agent"""
    data = request.get_json()

    required_fields = ['name', 'description', 'capabilities', 'tools', 'system_prompt']
    if not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if agent exists
    agent = db.get_custom_agent_by_id(agent_id)
    if not agent:
        return jsonify({'error': 'Custom agent not found'}), 404

    # Parse capabilities and tools
    capabilities = data['capabilities']
    if isinstance(capabilities, str):
        try:
            capabilities = json.loads(capabilities)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON in capabilities'}), 400

    tools = data['tools']
    if isinstance(tools, str):
        try:
            tools = json.loads(tools)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON in tools'}), 400

    # Parse config_schema if provided
    config_schema = data.get('config_schema')
    if config_schema and isinstance(config_schema, str):
        try:
            config_schema = json.loads(config_schema)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON in config_schema'}), 400

    db.update_custom_agent(
        agent_id=agent_id,
        name=data['name'],
        description=data['description'],
        capabilities=capabilities,
        tools=tools,
        system_prompt=data['system_prompt'],
        config_schema=config_schema
    )

    return jsonify({'message': 'Custom agent updated successfully'})

@app.route('/api/custom-agents/<int:agent_id>', methods=['DELETE'])
def delete_custom_agent(agent_id):
    """Delete custom agent"""
    db.delete_custom_agent(agent_id)
    return jsonify({'message': 'Custom agent deleted successfully'})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Agent Modes Database & GUI")
    print("="*50)
    print("\nServer starting on http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
