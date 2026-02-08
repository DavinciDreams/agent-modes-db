# Agent Modes Database - API Documentation

Complete API reference for the Agent Modes Database & GUI application.

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Error Handling](#error-handling)
4. [Core Endpoints](#core-endpoints)
5. [File Upload Endpoints](#file-upload-endpoints)
6. [Format Conversion Endpoints](#format-conversion-endpoints)
7. [Template Creation from Upload Endpoints](#template-creation-from-upload-endpoints)
8. [Agent Card Endpoints](#agent-card-endpoints)

---

## Overview

The Agent Modes Database API provides RESTful endpoints for managing agent templates, configurations, custom agents, file uploads, format conversions, and agent cards. All endpoints return JSON responses.

**Base URL:** `http://localhost:5000`

**Content-Type:** `application/json`

---

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data or parameters
- `403 Forbidden` - Operation not allowed (e.g., updating built-in templates)
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Error Response Format

```json
{
  "error": "Error message describing the issue"
}
```

For validation errors, additional details may be provided:

```json
{
  "error": "Validation failed",
  "errors": ["Specific error 1", "Specific error 2"]
}
```

---

## Core Endpoints

### Templates

#### Get All Templates

```http
GET /api/templates
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Code Explorer",
    "description": "Explore and analyze code structure",
    "category": "Development",
    "is_builtin": true,
    "created_at": "2024-01-01T00:00:00.000Z",
    "updated_at": "2024-01-01T00:00:00.000Z",
    "source_format": null,
    "source_file_id": null,
    "is_imported": false
  }
]
```

#### Get Specific Template

```http
GET /api/templates/<id>
```

**Response:**
```json
{
  "id": 1,
  "name": "Code Explorer",
  "description": "Explore and analyze code structure",
  "category": "Development",
  "is_builtin": true,
  "created_at": "2024-01-01T00:00:00.000Z",
  "updated_at": "2024-01-01T00:00:00.000Z",
  "source_format": null,
  "source_file_id": null,
  "is_imported": false
}
```

#### Create Template

```http
POST /api/templates
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "My Template",
  "description": "A custom template",
  "category": "Custom",
  "is_builtin": false
}
```

**Response (201):**
```json
{
  "id": 6,
  "message": "Template created successfully"
}
```

#### Update Template

```http
PUT /api/templates/<id>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Updated Template Name",
  "description": "Updated description",
  "category": "Updated Category"
}
```

**Response:**
```json
{
  "message": "Template updated successfully"
}
```

**Note:** Built-in templates cannot be updated (returns 403).

#### Delete Template

```http
DELETE /api/templates/<id>
```

**Response:**
```json
{
  "message": "Template deleted successfully"
}
```

**Note:** Built-in templates cannot be deleted (returns 403).

---

### Configurations

#### Get All Configurations

```http
GET /api/configurations
```

**Response:**
```json
[
  {
    "id": 1,
    "template_id": 1,
    "name": "My Configuration",
    "config_json": "{\"key\": \"value\"}",
    "created_at": "2024-01-01T00:00:00.000Z",
    "updated_at": "2024-01-01T00:00:00.000Z"
  }
]
```

#### Get Specific Configuration

```http
GET /api/configurations/<id>
```

**Response:**
```json
{
  "id": 1,
  "template_id": 1,
  "name": "My Configuration",
  "config_json": "{\"key\": \"value\"}",
  "created_at": "2024-01-01T00:00:00.000Z",
  "updated_at": "2024-01-01T00:00:00.000Z"
}
```

#### Create Configuration

```http
POST /api/configurations
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "My Configuration",
  "template_id": 1,
  "config_json": {
    "key": "value"
  }
}
```

**Response (201):**
```json
{
  "id": 1,
  "message": "Configuration created successfully"
}
```

#### Update Configuration

```http
PUT /api/configurations/<id>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Updated Configuration",
  "template_id": 1,
  "config_json": {
    "key": "updated_value"
  }
}
```

**Response:**
```json
{
  "message": "Configuration updated successfully"
}
```

#### Delete Configuration

```http
DELETE /api/configurations/<id>
```

**Response:**
```json
{
  "message": "Configuration deleted successfully"
}
```

---

### Custom Agents

#### Get All Custom Agents

```http
GET /api/custom-agents
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "My Custom Agent",
    "description": "A custom agent",
    "capabilities": ["capability1", "capability2"],
    "tools": ["tool1", "tool2"],
    "system_prompt": "You are a helpful assistant.",
    "config_schema": null,
    "created_at": "2024-01-01T00:00:00.000Z",
    "updated_at": "2024-01-01T00:00:00.000Z",
    "source_format": null,
    "source_file_id": null,
    "is_imported": false
  }
]
```

#### Get Specific Custom Agent

```http
GET /api/custom-agents/<id>
```

**Response:**
```json
{
  "id": 1,
  "name": "My Custom Agent",
  "description": "A custom agent",
  "capabilities": ["capability1", "capability2"],
  "tools": ["tool1", "tool2"],
  "system_prompt": "You are a helpful assistant.",
  "config_schema": null,
  "created_at": "2024-01-01T00:00:00.000Z",
  "updated_at": "2024-01-01T00:00:00.000Z",
  "source_format": null,
  "source_file_id": null,
  "is_imported": false
}
```

#### Create Custom Agent

```http
POST /api/custom-agents
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "My Custom Agent",
  "description": "A custom agent",
  "capabilities": ["capability1", "capability2"],
  "tools": ["tool1", "tool2"],
  "system_prompt": "You are a helpful assistant.",
  "config_schema": {
    "type": "object",
    "properties": {
      "param1": {"type": "string"}
    }
  }
}
```

**Response (201):**
```json
{
  "id": 1,
  "message": "Custom agent created successfully"
}
```

#### Update Custom Agent

```http
PUT /api/custom-agents/<id>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Updated Agent Name",
  "description": "Updated description",
  "capabilities": ["capability1", "capability2", "capability3"],
  "tools": ["tool1", "tool2"],
  "system_prompt": "You are an updated helpful assistant.",
  "config_schema": {
    "type": "object",
    "properties": {
      "param1": {"type": "string"},
      "param2": {"type": "number"}
    }
  }
}
```

**Response:**
```json
{
  "message": "Custom agent updated successfully"
}
```

#### Delete Custom Agent

```http
DELETE /api/custom-agents/<id>
```

**Response:**
```json
{
  "message": "Custom agent deleted successfully"
}
```

---

## File Upload Endpoints

### Upload Single File

```http
POST /api/files/upload
Content-Type: multipart/form-data
```

**Request Parameters:**
- `file` (file, required): The agent definition file to upload

**Supported Formats:** YAML (.yaml, .yml), JSON (.json), Markdown (.md)

**Response (201):**
```json
{
  "upload_id": 1,
  "filename": "agent_definition.yaml",
  "original_filename": "my_agent.yaml",
  "file_format": "yaml",
  "file_size": 1024,
  "upload_status": "completed",
  "parse_result": {
    "name": "Agent Name",
    "description": "Agent description",
    "capabilities": ["cap1", "cap2"]
  },
  "uploaded_at": "2024-01-01T00:00:00.000Z"
}
```

**Error Response (400):**
```json
{
  "error": "Invalid file format. Supported formats: YAML, JSON, MD"
}
```

### Upload Multiple Files

```http
POST /api/files/upload/multiple
Content-Type: multipart/form-data
```

**Request Parameters:**
- `files` (file[], required): Multiple agent definition files to upload

**Response (201):**
```json
{
  "uploads": [
    {
      "upload_id": 1,
      "filename": "agent1.yaml",
      "original_filename": "agent1.yaml",
      "file_format": "yaml",
      "status": "completed",
      "parse_result": {...}
    },
    {
      "filename": "agent2.json",
      "original_filename": "agent2.json",
      "status": "failed",
      "error": "Validation failed"
    }
  ],
  "total": 2,
  "successful": 1,
  "failed": 1
}
```

### Get All File Uploads

```http
GET /api/files?status=completed&format=yaml
```

**Query Parameters:**
- `status` (optional): Filter by upload status (pending, processing, completed, failed)
- `format` (optional): Filter by file format (yaml, json, md)

**Response:**
```json
{
  "uploads": [
    {
      "id": 1,
      "filename": "agent_definition.yaml",
      "original_filename": "my_agent.yaml",
      "file_format": "yaml",
      "file_size": 1024,
      "upload_status": "completed",
      "uploaded_at": "2024-01-01T00:00:00.000Z"
    }
  ],
  "total": 1
}
```

### Get Specific File Upload

```http
GET /api/files/<upload_id>
```

**Response:**
```json
{
  "id": 1,
  "upload_id": 1,
  "filename": "agent_definition.yaml",
  "original_filename": "my_agent.yaml",
  "file_format": "yaml",
  "file_size": 1024,
  "upload_status": "completed",
  "parse_result": {
    "name": "Agent Name",
    "description": "Agent description"
  },
  "uploaded_at": "2024-01-01T00:00:00.000Z"
}
```

### Delete File Upload

```http
DELETE /api/files/<upload_id>
```

**Response:**
```json
{
  "message": "File upload deleted successfully"
}
```

---

## Format Conversion Endpoints

### Convert Agent Definition

```http
POST /api/convert
Content-Type: application/json
```

**Request Body:**
```json
{
  "source_format": "claude",
  "target_format": "roo",
  "agent_data": {
    "name": "Agent Name",
    "description": "Agent description",
    "capabilities": ["cap1", "cap2"]
  }
}
```

**Supported Formats:** claude, roo, custom

**Response (200):**
```json
{
  "conversion_id": 1,
  "source_format": "claude",
  "target_format": "roo",
  "source_data": {...},
  "target_data": {
    "name": "Agent Name",
    "description": "Agent description",
    "capabilities": ["cap1", "cap2"]
  },
  "conversion_status": "success",
  "warnings": [],
  "created_at": "2024-01-01T00:00:00.000Z"
}
```

**Error Response (400):**
```json
{
  "error": "Invalid conversion",
  "errors": ["Source format 'invalid' is not supported"]
}
```

### Convert Uploaded File

```http
POST /api/convert/file
Content-Type: application/json
```

**Request Body:**
```json
{
  "upload_id": 1,
  "target_format": "roo",
  "source_format": "claude"
}
```

**Note:** `source_format` is optional. If not provided, it will be auto-detected.

**Response (200):**
```json
{
  "conversion_id": 1,
  "source_format": "claude",
  "target_format": "roo",
  "target_data": {
    "name": "Agent Name",
    "description": "Agent description"
  },
  "conversion_status": "success",
  "warnings": [],
  "created_at": "2024-01-01T00:00:00.000Z"
}
```

### Get Conversion History

```http
GET /api/convert/history?source_format=claude&target_format=roo&limit=50
```

**Query Parameters:**
- `source_format` (optional): Filter by source format
- `target_format` (optional): Filter by target format
- `limit` (optional): Maximum number of results (default: 50)

**Response:**
```json
{
  "conversions": [
    {
      "id": 1,
      "source_format": "claude",
      "target_format": "roo",
      "source_data": {...},
      "target_data": {...},
      "conversion_status": "success",
      "created_at": "2024-01-01T00:00:00.000Z"
    }
  ],
  "total": 1
}
```

### Get Supported Formats

```http
GET /api/convert/formats
```

**Response:**
```json
{
  "formats": ["claude", "roo", "custom"]
}
```

---

## Template Creation from Upload Endpoints

### Create Template from Upload

```http
POST /api/templates/from-upload
Content-Type: application/json
```

**Request Body:**
```json
{
  "upload_id": 1,
  "name": "Imported Template",
  "description": "Template created from uploaded file",
  "category": "Imported",
  "edit_data": {
    "description": "Override description"
  }
}
```

**Note:** `edit_data` is optional and allows overriding fields from the uploaded data.

**Response (201):**
```json
{
  "id": 6,
  "name": "Imported Template",
  "description": "Template created from uploaded file",
  "category": "Imported",
  "source_format": "claude",
  "source_file_id": 1,
  "is_imported": true,
  "message": "Template created successfully from uploaded file"
}
```

### Create Template from Data

```http
POST /api/templates/from-data
Content-Type: application/json
```

**Request Body:**
```json
{
  "source_format": "claude",
  "agent_data": {
    "name": "Agent Name",
    "description": "Agent description",
    "capabilities": ["cap1", "cap2"]
  },
  "name": "My Template",
  "description": "Template description",
  "category": "Custom"
}
```

**Response (201):**
```json
{
  "id": 6,
  "name": "My Template",
  "description": "Template description",
  "category": "Custom",
  "source_format": "claude",
  "is_imported": true,
  "message": "Template created successfully from agent data"
}
```

---

## Agent Card Endpoints

### Get All Agent Cards

```http
GET /api/agent-cards?entity_type=template&published=true
```

**Query Parameters:**
- `entity_type` (optional): Filter by entity type (template, configuration, custom_agent)
- `published` (optional): Filter by published status (true/false)

**Response:**
```json
{
  "cards": [
    {
      "id": 1,
      "entity_type": "template",
      "entity_id": 1,
      "card_data": {
        "name": "Code Explorer",
        "description": "Explore and analyze code structure",
        "version": "1.0"
      },
      "card_version": "1.0",
      "published": true,
      "generated_at": "2024-01-01T00:00:00.000Z",
      "updated_at": "2024-01-01T00:00:00.000Z"
    }
  ],
  "total": 1
}
```

### Get Specific Agent Card

```http
GET /api/agent-cards/<card_id>
```

**Response:**
```json
{
  "id": 1,
  "entity_type": "template",
  "entity_id": 1,
  "card_data": {
    "name": "Code Explorer",
    "description": "Explore and analyze code structure",
    "version": "1.0"
  },
  "card_version": "1.0",
  "published": true,
  "generated_at": "2024-01-01T00:00:00.000Z",
  "updated_at": "2024-01-01T00:00:00.000Z"
}
```

### Generate Agent Card

```http
POST /api/agent-cards/generate
Content-Type: application/json
```

**Request Body:**
```json
{
  "entity_type": "template",
  "entity_id": 1
}
```

**Entity Types:** template, configuration, custom_agent

**Response (201):**
```json
{
  "id": 1,
  "message": "Agent card generated successfully",
  "card": {
    "id": 1,
    "entity_type": "template",
    "entity_id": 1,
    "card_data": {
      "name": "Code Explorer",
      "description": "Explore and analyze code structure",
      "version": "1.0"
    },
    "card_version": "1.0",
    "published": false,
    "generated_at": "2024-01-01T00:00:00.000Z",
    "updated_at": "2024-01-01T00:00:00.000Z"
  }
}
```

**Note:** If a card already exists for the entity, it will be updated (200 status).

### Generate Multiple Agent Cards

```http
POST /api/agent-cards/generate/batch
Content-Type: application/json
```

**Request Body:**
```json
{
  "entities": [
    {
      "entity_type": "template",
      "entity_id": 1
    },
    {
      "entity_type": "configuration",
      "entity_id": 2
    },
    {
      "entity_type": "custom_agent",
      "entity_id": 3
    }
  ]
}
```

**Response (200):**
```json
{
  "results": [
    {
      "entity_type": "template",
      "entity_id": 1,
      "status": "created",
      "card_id": 1
    },
    {
      "entity_type": "configuration",
      "entity_id": 2,
      "status": "updated",
      "card_id": 2
    },
    {
      "entity_type": "custom_agent",
      "entity_id": 3,
      "status": "error",
      "error": "Custom agent not found"
    }
  ],
  "total": 3,
  "successful": 2,
  "failed": 1
}
```

### Update Agent Card

```http
PUT /api/agent-cards/<card_id>
Content-Type: application/json
```

**Request Body:**
```json
{
  "card_data": {
    "name": "Updated Card Name",
    "description": "Updated description"
  },
  "published": true
}
```

**Note:** Both `card_data` and `published` are optional. You can update one or both.

**Response:**
```json
{
  "message": "Agent card updated successfully",
  "card": {
    "id": 1,
    "entity_type": "template",
    "entity_id": 1,
    "card_data": {
      "name": "Updated Card Name",
      "description": "Updated description",
      "version": "1.0"
    },
    "card_version": "1.0",
    "published": true,
    "generated_at": "2024-01-01T00:00:00.000Z",
    "updated_at": "2024-01-01T01:00:00.000Z"
  }
}
```

### Delete Agent Card

```http
DELETE /api/agent-cards/<card_id>
```

**Response:**
```json
{
  "message": "Agent card deleted successfully"
}
```

### Export Agent Card

```http
GET /api/agent-cards/<card_id>/export?format=json
```

**Query Parameters:**
- `format` (optional): Export format - json or yaml (default: json)

**Response:**
```json
{
  "format": "json",
  "content": "{\"name\":\"Code Explorer\",\"description\":\"Explore and analyze code structure\",\"version\":\"1.0\"}",
  "filename": "agent-card-1.json"
}
```

### Validate Agent Card

```http
POST /api/agent-cards/<card_id>/validate
```

**Response:**
```json
{
  "valid": true,
  "errors": null
}
```

**Invalid Card Response:**
```json
{
  "valid": false,
  "errors": [
    "Missing required field: name",
    "Invalid value for version"
  ]
}
```

---

## Examples

### Complete Workflow: Upload, Convert, and Create Template

```bash
# 1. Upload an agent definition file
curl -X POST http://localhost:5000/api/files/upload \
  -F "file=@my_agent.yaml"

# Response: {"upload_id": 1, ...}

# 2. Convert the uploaded file to a different format
curl -X POST http://localhost:5000/api/convert/file \
  -H "Content-Type: application/json" \
  -d '{"upload_id": 1, "target_format": "roo"}'

# Response: {"conversion_id": 1, "target_data": {...}, ...}

# 3. Create a template from the uploaded file
curl -X POST http://localhost:5000/api/templates/from-upload \
  -H "Content-Type: application/json" \
  -d '{
    "upload_id": 1,
    "name": "My Imported Template",
    "description": "Template from uploaded file",
    "category": "Imported"
  }'

# Response: {"id": 6, "message": "Template created successfully from uploaded file", ...}
```

### Generate and Export Agent Card

```bash
# 1. Generate an agent card from a template
curl -X POST http://localhost:5000/api/agent-cards/generate \
  -H "Content-Type: application/json" \
  -d '{"entity_type": "template", "entity_id": 1}'

# Response: {"id": 1, "message": "Agent card generated successfully", ...}

# 2. Export the agent card as YAML
curl -X GET "http://localhost:5000/api/agent-cards/1/export?format=yaml"

# Response: {"format": "yaml", "content": "name: Code Explorer\ndescription: ...", "filename": "agent-card-1.yaml"}
```

---

## Support

For issues or questions about the API, please refer to:
- [README.md](README.md) - Project overview and quick start
- [USER_GUIDE.md](USER_GUIDE.md) - Detailed user guide
- [MIGRATION.md](MIGRATION.md) - Database migration guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines
