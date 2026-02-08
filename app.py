from flask import Flask, request, jsonify, render_template
import database as db
import json
import os
import parsers
import utils
import converters
from converters import UniversalConverter

app = Flask(__name__)

# Initialize database on first run
# On Vercel, database is in /tmp and needs to be initialized on every cold start
db_path = db.DB_FILE if hasattr(db, 'DB_FILE') else 'agents.db'
if not os.path.exists(db_path):
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

    print(f"TEMPLATE DEBUG: Created template with id={template_id}")
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

# ============================================
# File Uploads API
# ============================================

@app.route('/api/files/upload', methods=['POST'])
def upload_file():
    """
    Upload a single agent definition file.
    
    Expected: multipart/form-data with 'file' field
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file format
    original_filename = file.filename
    if not utils.is_valid_file_format(original_filename):
        return jsonify({'error': 'Invalid file format. Supported formats: YAML, JSON, MD'}), 400
    
    # Read file content
    try:
        content = file.read().decode('utf-8')
    except UnicodeDecodeError:
        return jsonify({'error': 'File encoding error. Please use UTF-8 encoding'}), 400
    
    # Detect file format
    file_format = parsers.detect_format(original_filename, content)
    if file_format == 'unknown':
        return jsonify({'error': 'Could not detect file format'}), 400
    
    # Parse file content
    try:
        parser = parsers.get_parser(file_format)
        parsed_data = parser.parse(content)
        
        # Validate parsed data
        is_valid, errors = parser.validate(parsed_data)
        if not is_valid:
            return jsonify({'error': 'Validation failed', 'errors': errors}), 400
        
        # Normalize agent data
        normalized_data = utils.normalize_agent_data(parsed_data)
        
        # Detect agent format
        agent_format = parsers.detect_agent_format(content)
        
        # Generate stored filename
        stored_filename = utils.sanitize_filename(original_filename)
        
        # Create file upload record
        upload_id = db.create_file_upload(
            filename=stored_filename,
            original_filename=original_filename,
            file_format=file_format,
            file_size=len(content.encode('utf-8')),
            upload_status='completed',
            parse_result=normalized_data
        )
        
        # Get the created upload
        upload = db.get_file_upload_by_id(upload_id)
        
        # Prepare response
        response = {
            'upload_id': upload_id,
            'filename': upload['filename'],
            'original_filename': upload['original_filename'],
            'file_format': upload['file_format'],
            'file_size': upload['file_size'],
            'upload_status': upload['upload_status'],
            'parse_result': json.loads(upload['parse_result']) if upload['parse_result'] else None,
            'uploaded_at': upload['uploaded_at']
        }
        
        return jsonify(response), 201
        
    except ValueError as e:
        # Create failed upload record
        stored_filename = utils.sanitize_filename(original_filename)
        file_format = parsers.detect_format(original_filename)
        db.create_file_upload(
            filename=stored_filename,
            original_filename=original_filename,
            file_format=file_format,
            file_size=len(content.encode('utf-8')),
            upload_status='failed',
            error_message=str(e)
        )
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500


@app.route('/api/files/upload/multiple', methods=['POST'])
def upload_multiple_files():
    """
    Upload multiple agent definition files.
    
    Expected: multipart/form-data with 'files' field (multiple files)
    """
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No files selected'}), 400
    
    results = []
    successful = 0
    failed = 0
    
    for file in files:
        if file.filename == '':
            continue
        
        original_filename = file.filename
        
        # Validate file format
        if not utils.is_valid_file_format(original_filename):
            results.append({
                'filename': original_filename,
                'status': 'failed',
                'error': 'Invalid file format'
            })
            failed += 1
            continue
        
        # Read file content
        try:
            content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            results.append({
                'filename': original_filename,
                'status': 'failed',
                'error': 'File encoding error'
            })
            failed += 1
            continue
        
        # Detect file format
        file_format = parsers.detect_format(original_filename, content)
        if file_format == 'unknown':
            results.append({
                'filename': original_filename,
                'status': 'failed',
                'error': 'Could not detect file format'
            })
            failed += 1
            continue
        
        # Parse file content
        try:
            parser = parsers.get_parser(file_format)
            parsed_data = parser.parse(content)
            
            # Validate parsed data
            is_valid, errors = parser.validate(parsed_data)
            if not is_valid:
                results.append({
                    'filename': original_filename,
                    'status': 'failed',
                    'error': 'Validation failed',
                    'errors': errors
                })
                failed += 1
                continue
            
            # Normalize agent data
            normalized_data = utils.normalize_agent_data(parsed_data)
            
            # Generate stored filename
            stored_filename = utils.sanitize_filename(original_filename)
            
            # Create file upload record
            upload_id = db.create_file_upload(
                filename=stored_filename,
                original_filename=original_filename,
                file_format=file_format,
                file_size=len(content.encode('utf-8')),
                upload_status='completed',
                parse_result=normalized_data
            )
            
            results.append({
                'upload_id': upload_id,
                'filename': stored_filename,
                'original_filename': original_filename,
                'file_format': file_format,
                'status': 'completed',
                'parse_result': normalized_data
            })
            successful += 1
            
        except ValueError as e:
            stored_filename = utils.sanitize_filename(original_filename)
            file_format = parsers.detect_format(original_filename)
            db.create_file_upload(
                filename=stored_filename,
                original_filename=original_filename,
                file_format=file_format,
                file_size=len(content.encode('utf-8')),
                upload_status='failed',
                error_message=str(e)
            )
            results.append({
                'filename': original_filename,
                'status': 'failed',
                'error': str(e)
            })
            failed += 1
        except Exception as e:
            results.append({
                'filename': original_filename,
                'status': 'failed',
                'error': f'Error processing file: {str(e)}'
            })
            failed += 1
    
    return jsonify({
        'uploads': results,
        'total': len(results),
        'successful': successful,
        'failed': failed
    }), 201


@app.route('/api/files', methods=['GET'])
def get_file_uploads():
    """
    Get all file uploads with optional filtering.
    
    Query parameters:
        status: Filter by upload status (optional)
        format: Filter by file format (optional)
    """
    status = request.args.get('status')
    file_format = request.args.get('format')
    
    uploads = db.get_all_file_uploads(status=status, file_format=file_format)
    
    return jsonify({
        'uploads': uploads,
        'total': len(uploads)
    })


@app.route('/api/files/<int:upload_id>', methods=['GET'])
def get_file_upload(upload_id):
    """
    Get details of a specific file upload.
    """
    upload = db.get_file_upload_by_id(upload_id)
    
    if not upload:
        return jsonify({'error': 'File upload not found'}), 404
    
    # Parse parse_result if it exists
    if upload.get('parse_result'):
        upload['parse_result'] = json.loads(upload['parse_result'])
    
    # Add upload_id field for consistency with POST endpoint
    upload['upload_id'] = upload['id']
    
    return jsonify(upload)


@app.route('/api/files/<int:upload_id>', methods=['DELETE'])
def delete_file_upload(upload_id):
    """
    Delete a file upload record.
    """
    upload = db.get_file_upload_by_id(upload_id)
    
    if not upload:
        return jsonify({'error': 'File upload not found'}), 404
    
    db.delete_file_upload(upload_id)
    
    return jsonify({'message': 'File upload deleted successfully'})

# ============================================
# Format Conversion API
# ============================================

@app.route('/api/convert', methods=['POST'])
def convert_agent():
    """
    Convert agent definition between formats.
    
    Expected: JSON with source_format, target_format, and agent_data
    """
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['source_format', 'target_format', 'agent_data']):
        return jsonify({'error': 'Missing required fields: source_format, target_format, agent_data'}), 400
    
    source_format = data['source_format']
    target_format = data['target_format']
    agent_data = data['agent_data']
    
    # Validate conversion
    is_valid, errors = UniversalConverter.validate_conversion(source_format, target_format)
    if not is_valid:
        return jsonify({'error': 'Invalid conversion', 'errors': errors}), 400
    
    # Perform conversion
    try:
        target_data, warnings = UniversalConverter.convert(
            source_data=agent_data,
            source_format=source_format,
            target_format=target_format
        )
        
        # Store conversion in database
        conversion_id = db.create_format_conversion(
            source_format=source_format,
            target_format=target_format,
            source_data=agent_data,
            target_data=target_data,
            conversion_status='success'
        )
        
        # Get the created conversion
        conversion = db.get_format_conversion_by_id(conversion_id)
        
        # Prepare response
        response = {
            'conversion_id': conversion_id,
            'source_format': source_format,
            'target_format': target_format,
            'source_data': agent_data,
            'target_data': target_data,
            'conversion_status': 'success',
            'warnings': warnings,
            'created_at': conversion['created_at']
        }
        
        return jsonify(response), 200
        
    except ValueError as e:
        # Store failed conversion
        db.create_format_conversion(
            source_format=source_format,
            target_format=target_format,
            source_data=agent_data,
            target_data={},
            conversion_status='failed',
            error_message=str(e)
        )
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Conversion error: {str(e)}'}), 500


@app.route('/api/convert/file', methods=['POST'])
def convert_file():
    """
    Convert an uploaded file to a different format.
    
    Expected: JSON with upload_id and target_format
    """
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['upload_id', 'target_format']):
        return jsonify({'error': 'Missing required fields: upload_id, target_format'}), 400
    
    upload_id = data['upload_id']
    target_format = data['target_format']
    
    # Get file upload
    upload = db.get_file_upload_by_id(upload_id)
    if not upload:
        return jsonify({'error': 'File upload not found'}), 404
    
    # Check if upload was successful
    if upload['upload_status'] != 'completed':
        return jsonify({'error': 'File upload was not completed successfully'}), 400
    
    # Get parsed data
    parse_result = upload.get('parse_result')
    if not parse_result:
        return jsonify({'error': 'No parsed data available for this upload'}), 400
    
    # Parse parse_result if it's a string
    if isinstance(parse_result, str):
        try:
            source_data = json.loads(parse_result)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid parsed data in upload record'}), 400
    else:
        source_data = parse_result
    
    # Detect source format from file format or agent format
    source_format = data.get('source_format')
    if not source_format:
        # Try to detect from file format
        file_format = upload['file_format']
        if file_format in ['json', 'yaml', 'yml']:
            # Detect agent format from content
            source_format = parsers.detect_agent_format(json.dumps(source_data))
        else:
            return jsonify({'error': 'Cannot detect source format from this file type'}), 400
    
    # Validate conversion
    is_valid, errors = UniversalConverter.validate_conversion(source_format, target_format)
    if not is_valid:
        return jsonify({'error': 'Invalid conversion', 'errors': errors}), 400
    
    # Perform conversion
    try:
        target_data, warnings = UniversalConverter.convert(
            source_data=source_data,
            source_format=source_format,
            target_format=target_format
        )
        
        # Store conversion in database
        conversion_id = db.create_format_conversion(
            source_format=source_format,
            target_format=target_format,
            source_data=source_data,
            target_data=target_data,
            conversion_status='success'
        )
        
        # Get the created conversion
        conversion = db.get_format_conversion_by_id(conversion_id)
        
        # Prepare response
        response = {
            'conversion_id': conversion_id,
            'source_format': source_format,
            'target_format': target_format,
            'target_data': target_data,
            'conversion_status': 'success',
            'warnings': warnings,
            'created_at': conversion['created_at']
        }
        
        return jsonify(response), 200
        
    except ValueError as e:
        # Store failed conversion
        db.create_format_conversion(
            source_format=source_format,
            target_format=target_format,
            source_data=source_data,
            target_data={},
            conversion_status='failed',
            error_message=str(e)
        )
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Conversion error: {str(e)}'}), 500


@app.route('/api/convert/history', methods=['GET'])
def get_conversion_history():
    """
    Get conversion history.
    
    Query parameters:
        source_format: Filter by source format (optional)
        target_format: Filter by target format (optional)
        limit: Maximum number of results (default: 50)
    """
    source_format = request.args.get('source_format')
    target_format = request.args.get('target_format')
    limit = request.args.get('limit', type=int)
    
    # Get conversions
    conversions = db.get_conversions_by_formats(
        source_format=source_format,
        target_format=target_format,
        limit=limit or 50
    )
    
    # Parse JSON fields in conversions
    for conversion in conversions:
        if conversion.get('source_data'):
            try:
                conversion['source_data'] = json.loads(conversion['source_data'])
            except (json.JSONDecodeError, TypeError):
                pass
        if conversion.get('target_data'):
            try:
                conversion['target_data'] = json.loads(conversion['target_data'])
            except (json.JSONDecodeError, TypeError):
                pass
    
    return jsonify({
        'conversions': conversions,
        'total': len(conversions)
    })


@app.route('/api/convert/formats', methods=['GET'])
def get_supported_formats():
    """
    Get list of supported formats.
    """
    formats = UniversalConverter.get_supported_formats()
    
    return jsonify({
        'formats': formats
    })


# ============================================
# Template Creation from Upload API
# ============================================

@app.route('/api/templates/from-upload', methods=['POST'])
def create_template_from_upload():
    """
    Create a template from an uploaded file.
    
    Expected: JSON with upload_id, name, description, category, and optional edit_data
    """
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['upload_id', 'name', 'description', 'category']):
        return jsonify({'error': 'Missing required fields: upload_id, name, description, category'}), 400
    
    upload_id = data['upload_id']
    name = data['name']
    description = data['description']
    category = data['category']
    
    # Get file upload
    upload = db.get_file_upload_by_id(upload_id)
    if not upload:
        return jsonify({'error': 'File upload not found'}), 404
    
    # Check if upload was successful
    if upload['upload_status'] != 'completed':
        return jsonify({'error': 'File upload was not completed successfully'}), 400
    
    # Get parsed data
    parse_result = upload.get('parse_result')
    if not parse_result:
        return jsonify({'error': 'No parsed data available for this upload'}), 400
    
    # Parse parse_result if it's a string
    if isinstance(parse_result, str):
        try:
            agent_data = json.loads(parse_result)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid parsed data in upload record'}), 400
    else:
        agent_data = parse_result
    
    # Detect source format from file format
    file_format = upload['file_format']
    source_format = parsers.detect_agent_format(json.dumps(agent_data))
    
    # Apply edit_data if provided
    edit_data = data.get('edit_data', {})
    if edit_data:
        # Merge edit data into agent data
        agent_data.update(edit_data)
    
    # Create template
    try:
        template_id = db.create_template(
            name=name,
            description=description,
            category=category,
            is_builtin=False,
            source_format=source_format,
            source_file_id=upload_id,
            is_imported=True
        )
        
        # Get the created template
        template = db.get_template_by_id(template_id)
        
        return jsonify({
            'id': template_id,
            'name': template['name'],
            'description': template['description'],
            'category': template['category'],
            'source_format': template['source_format'],
            'source_file_id': template['source_file_id'],
            'is_imported': template['is_imported'],
            'message': 'Template created successfully from uploaded file'
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error creating template: {str(e)}'}), 500


@app.route('/api/templates/from-data', methods=['POST'])
def create_template_from_data():
    """
    Create a template from parsed agent data.
    
    Expected: JSON with source_format, agent_data, name, description, and category
    """
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['source_format', 'agent_data', 'name', 'description', 'category']):
        return jsonify({'error': 'Missing required fields: source_format, agent_data, name, description, category'}), 400
    
    source_format = data['source_format']
    agent_data = data['agent_data']
    name = data['name']
    description = data['description']
    category = data['category']
    
    # Validate source format
    if source_format not in ['claude', 'roo', 'custom']:
        return jsonify({'error': f'Invalid source format: {source_format}'}), 400
    
    # Create template
    try:
        template_id = db.create_template(
            name=name,
            description=description,
            category=category,
            is_builtin=False,
            source_format=source_format,
            source_file_id=None,
            is_imported=True
        )
        
        # Get the created template
        template = db.get_template_by_id(template_id)
        
        return jsonify({
            'id': template_id,
            'name': template['name'],
            'description': template['description'],
            'category': template['category'],
            'source_format': template['source_format'],
            'is_imported': template['is_imported'],
            'message': 'Template created successfully from agent data'
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error creating template: {str(e)}'}), 500


# ============================================
# Agent Cards API
# ============================================

@app.route('/api/agent-cards', methods=['GET'])
def get_agent_cards():
    """Get all agent cards with optional filtering"""
    entity_type = request.args.get('entity_type')
    published = request.args.get('published')
    
    # Convert published string to boolean if provided
    if published is not None:
        published = published.lower() in ['true', '1', 'yes']
    
    cards = db.get_all_agent_cards(entity_type=entity_type, published=published)
    return jsonify({
        'cards': cards,
        'total': len(cards)
    })

@app.route('/api/agent-cards/<int:card_id>', methods=['GET'])
def get_agent_card(card_id):
    """Get specific agent card"""
    card = db.get_agent_card_by_id(card_id)
    if not card:
        return jsonify({'error': 'Agent card not found'}), 404
    return jsonify(card)

@app.route('/api/agent-cards/generate', methods=['POST'])
def generate_agent_card():
    """Generate agent card from entity"""
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['entity_type', 'entity_id']):
        return jsonify({'error': 'Missing required fields: entity_type, entity_id'}), 400
    
    entity_type = data['entity_type']
    entity_id = data['entity_id']
    
    # Validate entity type
    if entity_type not in ['template', 'configuration', 'custom_agent']:
        return jsonify({'error': f'Invalid entity type: {entity_type}. Must be: template, configuration, or custom_agent'}), 400
    
    # Get entity data
    if entity_type == 'template':
        entity_data = db.get_template_by_id(entity_id)
    elif entity_type == 'configuration':
        entity_data = db.get_configuration_by_id(entity_id)
    elif entity_type == 'custom_agent':
        entity_data = db.get_custom_agent_by_id(entity_id)
    
    if not entity_data:
        return jsonify({'error': f'{entity_type.capitalize()} not found'}), 404
    
    # Generate agent card
    try:
        from generators import AgentCardGenerator
        
        if entity_type == 'template':
            card_data = AgentCardGenerator.generate_from_template(entity_data)
        elif entity_type == 'configuration':
            card_data = AgentCardGenerator.generate_from_configuration(entity_data)
        elif entity_type == 'custom_agent':
            card_data = AgentCardGenerator.generate_from_custom_agent(entity_data)
        
        # Validate card
        is_valid, errors = AgentCardGenerator.validate_card(card_data)
        if not is_valid:
            return jsonify({'error': 'Card validation failed', 'errors': errors}), 400
        
        # Check if card already exists
        existing_card = db.get_agent_card_by_entity(entity_type, entity_id)
        
        print(f"DEBUG: existing_card = {existing_card}")
        
        if existing_card:
            # Update existing card
            db.update_agent_card(existing_card['id'], card_data=card_data)
            card = db.get_agent_card_by_id(existing_card['id'])
            print(f"DEBUG: Updating existing card, returning 200")
            return jsonify({
                'id': card['id'],
                'message': 'Agent card updated successfully',
                'card': card
            })
        else:
            # Create new card
            print(f"DEBUG: Creating new card for entity_type={entity_type}, entity_id={entity_id}")
            card_id = db.create_agent_card(entity_type, entity_id, card_data)
            card = db.get_agent_card_by_id(card_id)
            print(f"DEBUG: Created card with id={card_id}, returning 201")
            return jsonify({
                'id': card_id,
                'message': 'Agent card generated successfully',
                'card': card
            }), 201
            
    except Exception as e:
        return jsonify({'error': f'Error generating agent card: {str(e)}'}), 500

@app.route('/api/agent-cards/generate/batch', methods=['POST'])
def generate_agent_cards_batch():
    """Generate multiple agent cards"""
    data = request.get_json()
    
    # Validate required fields
    if 'entities' not in data:
        return jsonify({'error': 'Missing required field: entities'}), 400
    
    entities = data['entities']
    if not isinstance(entities, list):
        return jsonify({'error': 'entities must be a list'}), 400
    
    results = []
    from generators import AgentCardGenerator
    
    for entity in entities:
        if not all(k in entity for k in ['entity_type', 'entity_id']):
            results.append({
                'entity_type': entity.get('entity_type'),
                'entity_id': entity.get('entity_id'),
                'status': 'error',
                'error': 'Missing required fields'
            })
            continue
        
        entity_type = entity['entity_type']
        entity_id = entity['entity_id']
        
        # Validate entity type
        if entity_type not in ['template', 'configuration', 'custom_agent']:
            results.append({
                'entity_type': entity_type,
                'entity_id': entity_id,
                'status': 'error',
                'error': f'Invalid entity type: {entity_type}'
            })
            continue
        
        # Get entity data
        try:
            if entity_type == 'template':
                entity_data = db.get_template_by_id(entity_id)
            elif entity_type == 'configuration':
                entity_data = db.get_configuration_by_id(entity_id)
            elif entity_type == 'custom_agent':
                entity_data = db.get_custom_agent_by_id(entity_id)
            
            if not entity_data:
                results.append({
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'status': 'error',
                    'error': f'{entity_type.capitalize()} not found'
                })
                continue
            
            # Generate agent card
            if entity_type == 'template':
                card_data = AgentCardGenerator.generate_from_template(entity_data)
            elif entity_type == 'configuration':
                card_data = AgentCardGenerator.generate_from_configuration(entity_data)
            elif entity_type == 'custom_agent':
                card_data = AgentCardGenerator.generate_from_custom_agent(entity_data)
            
            # Validate card
            is_valid, errors = AgentCardGenerator.validate_card(card_data)
            if not is_valid:
                results.append({
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'status': 'error',
                    'error': 'Card validation failed',
                    'errors': errors
                })
                continue
            
            # Check if card already exists
            existing_card = db.get_agent_card_by_entity(entity_type, entity_id)
            
            if existing_card:
                # Update existing card
                db.update_agent_card(existing_card['id'], card_data=card_data)
                results.append({
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'status': 'updated',
                    'card_id': existing_card['id']
                })
            else:
                # Create new card
                card_id = db.create_agent_card(entity_type, entity_id, card_data)
                results.append({
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'status': 'created',
                    'card_id': card_id
                })
                
        except Exception as e:
            results.append({
                'entity_type': entity_type,
                'entity_id': entity_id,
                'status': 'error',
                'error': str(e)
            })
    
    return jsonify({
        'results': results,
        'total': len(results),
        'successful': sum(1 for r in results if r['status'] in ['created', 'updated']),
        'failed': sum(1 for r in results if r['status'] == 'error')
    })

@app.route('/api/agent-cards/<int:card_id>', methods=['PUT'])
def update_agent_card(card_id):
    """Update existing agent card"""
    data = request.get_json()
    
    # Check if card exists
    card = db.get_agent_card_by_id(card_id)
    if not card:
        return jsonify({'error': 'Agent card not found'}), 404
    
    # Update card
    try:
        card_data = data.get('card_data')
        published = data.get('published')
        
        db.update_agent_card(card_id, card_data=card_data, published=published)
        
        # If card_data was updated, validate it
        if card_data:
            from generators import AgentCardGenerator
            is_valid, errors = AgentCardGenerator.validate_card(card_data)
            if not is_valid:
                return jsonify({'error': 'Card validation failed', 'errors': errors}), 400
        
        updated_card = db.get_agent_card_by_id(card_id)
        return jsonify({
            'message': 'Agent card updated successfully',
            'card': updated_card
        })
    except Exception as e:
        return jsonify({'error': f'Error updating agent card: {str(e)}'}), 500

@app.route('/api/agent-cards/<int:card_id>', methods=['DELETE'])
def delete_agent_card(card_id):
    """Delete agent card"""
    card = db.get_agent_card_by_id(card_id)
    if not card:
        return jsonify({'error': 'Agent card not found'}), 404
    
    try:
        db.delete_agent_card(card_id)
        return jsonify({'message': 'Agent card deleted successfully'})
    except Exception as e:
        return jsonify({'error': f'Error deleting agent card: {str(e)}'}), 500

@app.route('/api/agent-cards/<int:card_id>/export', methods=['GET'])
def export_agent_card(card_id):
    """Export agent card in specified format"""
    card = db.get_agent_card_by_id(card_id)
    if not card:
        return jsonify({'error': 'Agent card not found'}), 404
    
    # Get format parameter
    export_format = request.args.get('format', 'json').lower()
    
    if export_format not in ['json', 'yaml']:
        return jsonify({'error': f'Invalid export format: {export_format}. Supported formats: json, yaml'}), 400
    
    try:
        from generators import AgentCardGenerator
        
        # Export card
        content = AgentCardGenerator.export_card(card['card_data'], export_format)
        
        # Generate filename
        filename = f"agent-card-{card_id}.{export_format}"
        
        return jsonify({
            'format': export_format,
            'content': content,
            'filename': filename
        })
    except Exception as e:
        return jsonify({'error': f'Error exporting agent card: {str(e)}'}), 500

@app.route('/api/agent-cards/<int:card_id>/validate', methods=['POST'])
def validate_agent_card(card_id):
    """Validate agent card"""
    card = db.get_agent_card_by_id(card_id)
    if not card:
        return jsonify({'error': 'Agent card not found'}), 404
    
    try:
        from generators import AgentCardGenerator
        
        is_valid, errors = AgentCardGenerator.validate_card(card['card_data'])
        
        return jsonify({
            'valid': is_valid,
            'errors': errors if not is_valid else None
        })
    except Exception as e:
        return jsonify({'error': f'Error validating agent card: {str(e)}'}), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Agent Modes Database & GUI")
    print("="*50)
    print("\nServer starting on http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
