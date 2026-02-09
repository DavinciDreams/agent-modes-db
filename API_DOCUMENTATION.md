# REST API Documentation - Agents, Teams, and Ratings

## Overview

This document describes the REST API endpoints for managing agents, teams, and ratings in the Agent Modes Database.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, the API does not require authentication. Ratings use anonymous user identification based on IP address and user agent.

---

## Agents API

### GET /api/agents

Get all agents with optional filtering and sorting.

**Query Parameters:**
- `sort` (optional): Sort field - `rating`, `downloads`, `name`, `date`. Default: `rating`
- `order` (optional): Sort order - `asc`, `desc`. Default: `desc`
- `search` (optional): Search term to filter by name or description
- `limit` (optional): Maximum number of results (1-1000). Default: `100`

**Response:**
```json
{
  "agents": [
    {
      "id": 1,
      "slug": "code-helper",
      "name": "Code Helper",
      "description": "A helpful coding assistant",
      "instructions": "You are a helpful coding assistant...",
      "tools": ["Read", "Write", "Edit"],
      "skills": ["Python", "JavaScript"],
      "default_model": "sonnet",
      "max_turns": 50,
      "allowed_edit_patterns": null,
      "metadata": {
        "author": "User",
        "version": "1.0.0"
      },
      "source_format": null,
      "source_file_id": null,
      "download_count": 10,
      "rating_average": 4.5,
      "rating_count": 5,
      "is_public": 1,
      "created_at": "2026-02-09 04:50:44",
      "updated_at": "2026-02-09 04:50:44"
    }
  ],
  "total": 1
}
```

**Example:**
```bash
curl "http://localhost:5000/api/agents?sort=downloads&order=desc&limit=10"
```

---

### GET /api/agents/:id

Get specific agent details by ID.

**URL Parameters:**
- `id`: Agent ID (integer)

**Response:**
```json
{
  "id": 1,
  "slug": "code-helper",
  "name": "Code Helper",
  "description": "A helpful coding assistant",
  "instructions": "You are a helpful coding assistant...",
  "tools": ["Read", "Write", "Edit"],
  "skills": ["Python", "JavaScript"],
  "default_model": "sonnet",
  "max_turns": 50,
  "allowed_edit_patterns": null,
  "metadata": {
    "author": "User",
    "version": "1.0.0"
  },
  "download_count": 10,
  "rating_average": 4.5,
  "rating_count": 5,
  "ratings": [
    {
      "id": 1,
      "entity_type": "agent",
      "entity_id": 1,
      "user_identifier": "abc123...",
      "rating": 5,
      "review": "Excellent!",
      "created_at": "2026-02-09 04:50:44",
      "updated_at": "2026-02-09 04:50:44"
    }
  ],
  "created_at": "2026-02-09 04:50:44",
  "updated_at": "2026-02-09 04:50:44"
}
```

**Example:**
```bash
curl "http://localhost:5000/api/agents/1"
```

---

### POST /api/agents

Create a new agent.

**Request Body:**
```json
{
  "slug": "code-helper",
  "name": "Code Helper",
  "description": "A helpful coding assistant",
  "instructions": "You are a helpful coding assistant that can read, write, and edit files. Always explain your changes and follow best practices.",
  "tools": ["Read", "Write", "Edit", "Grep"],
  "skills": ["Python", "JavaScript", "Testing"],
  "default_model": "sonnet",
  "max_turns": 50,
  "allowed_edit_patterns": ["*.py", "*.js"],
  "metadata": {
    "author": "User Name",
    "version": "1.0.0"
  }
}
```

**Required Fields:**
- `slug`: Unique identifier (lowercase, alphanumeric, hyphens)
- `name`: Agent name
- `instructions`: Detailed instructions (min 50 characters)
- `tools`: Array of tool names

**Optional Fields:**
- `description`: Short description
- `skills`: Array of skill names
- `default_model`: Model to use (`sonnet`, `haiku`, `opus`)
- `max_turns`: Maximum conversation turns (1-1000)
- `allowed_edit_patterns`: Array of file patterns the agent can edit
- `metadata`: Additional metadata object
- `source_format`: Original format (`claude`, `roo`, `custom`)
- `source_file_id`: ID of source file upload

**Response:**
```json
{
  "id": 1,
  "slug": "code-helper",
  "name": "Code Helper",
  ...
}
```

**Status Codes:**
- `201 Created`: Agent created successfully
- `400 Bad Request`: Validation failed
- `409 Conflict`: Agent with this slug already exists
- `500 Internal Server Error`: Server error

**Example:**
```bash
curl -X POST "http://localhost:5000/api/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "code-helper",
    "name": "Code Helper",
    "description": "A helpful coding assistant",
    "instructions": "You are a helpful coding assistant that can read, write, and edit files. Always explain your changes.",
    "tools": ["Read", "Write", "Edit"],
    "skills": ["Python"],
    "default_model": "sonnet",
    "max_turns": 50
  }'
```

---

### GET /api/agents/:id/download

Download agent definition (tracks download count).

**URL Parameters:**
- `id`: Agent ID (integer)

**Query Parameters:**
- `format` (optional): Output format - `universal`, `claude`, `roo`. Default: `universal`

**Response:** Same as GET /api/agents/:id

**Example:**
```bash
curl "http://localhost:5000/api/agents/1/download?format=claude"
```

---

### POST /api/agents/:id/rate

Submit or update a rating for an agent.

**URL Parameters:**
- `id`: Agent ID (integer)

**Request Body:**
```json
{
  "rating": 5,
  "review": "Excellent agent! Very helpful for coding tasks."
}
```

**Fields:**
- `rating`: Integer between 1 and 5 (required)
- `review`: Text review (optional)

**Response:**
```json
{
  "message": "Rating submitted successfully",
  "rating_average": 4.5,
  "rating_count": 10
}
```

**Status Codes:**
- `200 OK`: Rating submitted successfully
- `400 Bad Request`: Invalid rating value
- `404 Not Found`: Agent not found
- `500 Internal Server Error`: Server error

**Example:**
```bash
curl -X POST "http://localhost:5000/api/agents/1/rate" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "review": "Excellent agent!"
  }'
```

---

## Teams API

### GET /api/teams

Get all teams with optional filtering and sorting.

**Query Parameters:**
- `sort` (optional): Sort field - `rating`, `downloads`, `name`, `date`. Default: `rating`
- `order` (optional): Sort order - `asc`, `desc`. Default: `desc`
- `search` (optional): Search term to filter by name or description
- `limit` (optional): Maximum number of results (1-1000). Default: `100`

**Response:**
```json
{
  "teams": [
    {
      "id": 1,
      "slug": "dev-team",
      "name": "Development Team",
      "description": "A team for software development",
      "version": "1.0.0",
      "orchestrator": "backend-dev",
      "agents": [
        {
          "slug": "backend-dev",
          "role": "Backend Developer",
          "priority": 1
        }
      ],
      "workflow": {
        "type": "sequential",
        "stages": [
          {
            "name": "Development",
            "agents": ["backend-dev"]
          }
        ]
      },
      "tools": ["Read", "Write", "Edit"],
      "skills": ["Python", "SQL"],
      "metadata": {
        "author": "User"
      },
      "download_count": 5,
      "rating_average": 4.0,
      "rating_count": 2,
      "created_at": "2026-02-09 04:50:44",
      "updated_at": "2026-02-09 04:50:44"
    }
  ],
  "total": 1
}
```

**Example:**
```bash
curl "http://localhost:5000/api/teams?sort=rating&order=desc"
```

---

### GET /api/teams/:id

Get specific team details by ID.

**URL Parameters:**
- `id`: Team ID (integer)

**Response:**
```json
{
  "id": 1,
  "slug": "dev-team",
  "name": "Development Team",
  "description": "A team for software development",
  "version": "1.0.0",
  "orchestrator": "backend-dev",
  "agents": [...],
  "workflow": {...},
  "tools": ["Read", "Write"],
  "skills": ["Python"],
  "metadata": {},
  "download_count": 5,
  "rating_average": 4.0,
  "rating_count": 2,
  "ratings": [
    {
      "id": 1,
      "entity_type": "team",
      "entity_id": 1,
      "user_identifier": "abc123...",
      "rating": 4,
      "review": "Great team!",
      "created_at": "2026-02-09 04:50:44",
      "updated_at": "2026-02-09 04:50:44"
    }
  ],
  "created_at": "2026-02-09 04:50:44",
  "updated_at": "2026-02-09 04:50:44"
}
```

**Example:**
```bash
curl "http://localhost:5000/api/teams/1"
```

---

### POST /api/teams

Create a new team.

**Request Body:**
```json
{
  "slug": "dev-team",
  "name": "Development Team",
  "description": "A team for full-stack development",
  "version": "1.0.0",
  "agents": [
    {
      "slug": "backend-dev",
      "role": "Backend Developer",
      "priority": 1
    },
    {
      "slug": "frontend-dev",
      "role": "Frontend Developer",
      "priority": 2
    }
  ],
  "orchestrator": "backend-dev",
  "workflow": {
    "type": "sequential",
    "stages": [
      {
        "name": "Backend Development",
        "agents": ["backend-dev"]
      },
      {
        "name": "Frontend Development",
        "agents": ["frontend-dev"]
      }
    ]
  },
  "tools": ["Read", "Write", "Edit"],
  "skills": ["Python", "JavaScript"],
  "metadata": {
    "author": "User Name",
    "purpose": "Full stack development"
  }
}
```

**Required Fields:**
- `slug`: Unique identifier (lowercase, alphanumeric, hyphens)
- `name`: Team name
- `agents`: Array of agent configurations

**Agent Configuration:**
- `slug`: Agent slug (required, must exist)
- `role`: Agent role in team (required)
- `priority`: Priority (optional, 0-100)

**Optional Fields:**
- `description`: Team description
- `version`: Version string
- `orchestrator`: Slug of orchestrating agent
- `workflow`: Workflow configuration
- `tools`: Shared tools for team
- `skills`: Shared skills for team
- `metadata`: Additional metadata

**Response:**
```json
{
  "id": 1,
  "slug": "dev-team",
  "name": "Development Team",
  ...
}
```

**Status Codes:**
- `201 Created`: Team created successfully
- `400 Bad Request`: Validation failed
- `409 Conflict`: Team with this slug already exists
- `500 Internal Server Error`: Server error

**Example:**
```bash
curl -X POST "http://localhost:5000/api/teams" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "dev-team",
    "name": "Development Team",
    "description": "A team for development",
    "agents": [
      {
        "slug": "backend-dev",
        "role": "Backend Developer",
        "priority": 1
      }
    ],
    "orchestrator": "backend-dev"
  }'
```

---

### GET /api/teams/:id/download

Download team package (tracks download count).

**URL Parameters:**
- `id`: Team ID (integer)

**Response:** Same as GET /api/teams/:id

**Example:**
```bash
curl "http://localhost:5000/api/teams/1/download"
```

---

### POST /api/teams/:id/rate

Submit or update a rating for a team.

**URL Parameters:**
- `id`: Team ID (integer)

**Request Body:**
```json
{
  "rating": 4,
  "review": "Great team setup! Works well together."
}
```

**Fields:**
- `rating`: Integer between 1 and 5 (required)
- `review`: Text review (optional)

**Response:**
```json
{
  "message": "Rating submitted successfully",
  "rating_average": 4.2,
  "rating_count": 5
}
```

**Status Codes:**
- `200 OK`: Rating submitted successfully
- `400 Bad Request`: Invalid rating value
- `404 Not Found`: Team not found
- `500 Internal Server Error`: Server error

**Example:**
```bash
curl -X POST "http://localhost:5000/api/teams/1/rate" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 4,
    "review": "Great team!"
  }'
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "message": "Detailed error information"
}
```

**Common Error Codes:**
- `400 Bad Request`: Invalid input or validation failed
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `500 Internal Server Error`: Server error

---

## Validation Rules

### Agent Validation

- **slug**: 3-100 characters, lowercase alphanumeric and hyphens only
- **name**: 2-255 characters
- **instructions**: 50-10000 characters
- **tools**: At least 1 valid tool required
- **default_model**: Must be `sonnet`, `haiku`, or `opus`
- **max_turns**: Integer between 1 and 1000

**Valid Tools:**
- Read, Write, Edit, Glob, Grep, Bash, Task, TodoWrite

### Team Validation

- **slug**: 3-100 characters, lowercase alphanumeric and hyphens only
- **name**: 2-255 characters
- **agents**: 1-50 agents required
- **orchestrator**: Must be a slug of an agent in the team
- **workflow.type**: Must be `sequential`, `parallel`, or `orchestrated`

---

## Usage Examples

### Complete Agent Creation and Rating Flow

```bash
# 1. Create an agent
curl -X POST "http://localhost:5000/api/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "code-reviewer",
    "name": "Code Reviewer",
    "description": "Reviews code for quality and best practices",
    "instructions": "You are a code reviewer. Review code for quality, style, security, and best practices. Provide constructive feedback.",
    "tools": ["Read", "Grep"],
    "skills": ["Code Review", "Python", "JavaScript"],
    "default_model": "sonnet",
    "max_turns": 50
  }'

# 2. Rate the agent
curl -X POST "http://localhost:5000/api/agents/1/rate" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "review": "Excellent code reviewer!"
  }'

# 3. Download the agent
curl "http://localhost:5000/api/agents/1/download"
```

### Complete Team Creation and Rating Flow

```bash
# 1. Create a team
curl -X POST "http://localhost:5000/api/teams" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "code-quality-team",
    "name": "Code Quality Team",
    "description": "Team for code review and quality assurance",
    "agents": [
      {
        "slug": "code-reviewer",
        "role": "Code Reviewer",
        "priority": 1
      }
    ],
    "orchestrator": "code-reviewer",
    "workflow": {
      "type": "sequential",
      "stages": [
        {
          "name": "Code Review",
          "agents": ["code-reviewer"]
        }
      ]
    }
  }'

# 2. Rate the team
curl -X POST "http://localhost:5000/api/teams/1/rate" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 4,
    "review": "Great team for code quality!"
  }'

# 3. Download the team
curl "http://localhost:5000/api/teams/1/download"
```

---

## Database Schema

### Agents Table

```sql
CREATE TABLE agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    instructions TEXT NOT NULL,
    tools TEXT NOT NULL,  -- JSON array
    skills TEXT,  -- JSON array
    default_model TEXT DEFAULT 'sonnet',
    max_turns INTEGER DEFAULT 50,
    allowed_edit_patterns TEXT,  -- JSON array
    metadata TEXT,  -- JSON object
    source_format TEXT,
    source_file_id INTEGER,
    download_count INTEGER NOT NULL DEFAULT 0,
    rating_average REAL,
    rating_count INTEGER NOT NULL DEFAULT 0,
    is_public BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Teams Table

```sql
CREATE TABLE teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    version TEXT DEFAULT '1.0.0',
    orchestrator TEXT,
    agents_config TEXT NOT NULL,  -- JSON array
    workflow TEXT,  -- JSON object
    tools TEXT,  -- JSON array
    skills TEXT,  -- JSON array
    metadata TEXT,  -- JSON object
    download_count INTEGER NOT NULL DEFAULT 0,
    rating_average REAL,
    rating_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Ratings Table

```sql
CREATE TABLE ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,  -- 'agent' or 'team'
    entity_id INTEGER NOT NULL,
    user_identifier TEXT NOT NULL,  -- Anonymous hash
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_type, entity_id, user_identifier)
);
```

---

## Implementation Files

### Database Functions

**File:** `C:\Users\lmwat\agent-modes-db\database.py`

Key functions added:
- `get_all_agents(sort_by, order, search, limit)`
- `get_agent_by_id(agent_id)`
- `get_agent_by_slug(slug)`
- `create_agent(...)`
- `update_agent(agent_id, **kwargs)`
- `delete_agent(agent_id)`
- `increment_agent_downloads(agent_id)`
- `agent_exists(slug)`
- `get_all_teams(...)`
- `get_team_by_id(team_id)`
- `get_team_by_slug(slug)`
- `create_team(...)`
- `increment_team_downloads(team_id)`
- `create_or_update_rating(...)`
- `update_rating_average(entity_type, entity_id)`
- `get_ratings_for_entity(entity_type, entity_id)`

### API Endpoints

**File:** `C:\Users\lmwat\agent-modes-db\app.py`

Endpoints added:
- GET/POST `/api/agents`
- GET `/api/agents/:id`
- GET `/api/agents/:id/download`
- POST `/api/agents/:id/rate`
- GET/POST `/api/teams`
- GET `/api/teams/:id`
- GET `/api/teams/:id/download`
- POST `/api/teams/:id/rate`

### Validators

**File:** `C:\Users\lmwat\agent-modes-db\validators\agent_validator.py`
**File:** `C:\Users\lmwat\agent-modes-db\validators\team_validator.py`

Validation functions integrated into API endpoints.

---

## Notes

- Ratings use anonymous user identification (hash of IP + User-Agent)
- Download counts are incremented on each download request
- All JSON fields are automatically parsed/serialized
- Both SQLite and PostgreSQL are supported
- Migration `004_add_agents_teams.sql` creates the required tables
