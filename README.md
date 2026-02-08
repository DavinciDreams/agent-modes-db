# Agent Modes Database & GUI

A comprehensive web-based management system for agent configurations, templates, and custom agent definitions with advanced file upload, format conversion, and agent card generation capabilities. Built with Flask and vanilla JavaScript.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

## Features

### Core Features
- **Agent Templates**: Browse and manage pre-built agent templates
- **Configurations**: Create and edit agent configurations with JSON editor
- **Custom Agents**: Define your own agent types with capabilities, tools, and system prompts
- **REST API**: Full CRUD operations via RESTful API
- **Modern UI**: Responsive interface with Bootstrap 5
- **SQLite Database**: Lightweight, file-based storage

### New Features (Phases 1-4)

#### Phase 1: File Upload & Parsing
- **Drag & Drop Upload**: Intuitive drag and drop interface for uploading agent definition files
- **Multi-Format Support**: Import files in YAML, JSON, and Markdown formats
- **File Validation**: Automatic format detection and content validation
- **Upload History**: Track all uploaded files with status and parsing results
- **Batch Upload**: Upload multiple files simultaneously

#### Phase 2: Format Conversion
- **Universal Converter**: Convert agent definitions between Claude, Roo, and Custom formats
- **Intermediate Representation**: Normalized format for seamless conversions
- **Format Detection**: Automatic detection of source agent format
- **Conversion History**: Track all format conversions with audit trail
- **Template Creation**: Create templates directly from uploaded agent files

#### Phase 3: Agent Card Generation
- **Microsoft Discoverability**: Generate standardized agent cards for Microsoft ecosystem
- **Auto-Generation**: Automatically generate cards from templates, configurations, and custom agents
- **Card Validation**: Ensure generated cards meet Microsoft's agent card schema
- **Export Options**: Export agent cards in JSON or YAML formats
- **Batch Generation**: Generate multiple agent cards at once

#### Phase 4: Enhanced UI
- **Import & Convert Tab**: Dedicated interface for file upload and format conversion
- **Agent Card Preview**: Preview generated agent cards with validation status
- **Real-time Feedback**: Toast notifications and loading states for all operations
- **Responsive Design**: Fully responsive interface optimized for all screen sizes

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/agent-modes-db.git
cd agent-modes-db
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

The application requires the following dependencies:
- **Flask 3.0.0**: Web framework
- **PyYAML 6.0.1**: YAML file parsing
- **python-magic**: File type detection (with binary for Windows)

### Running the Application

Start the server:
```bash
python app.py
```

Open your browser and navigate to:
```
http://localhost:5000
```

### Database Initialization

The database is automatically initialized with seed data on first run. If you need to apply database migrations manually, see the [Migration Guide](#migration-guide) section below.

To reset the database, simply delete `agents.db` and restart the application.

## Usage

### Templates Tab
- View 5 built-in agent templates (Code Explorer, Test Runner, Documentation Generator, Bug Fixer, Code Reviewer)
- Create custom templates
- Filter by category
- Edit and delete custom templates (built-in templates are protected)
- View source format and import status for imported templates

### Configurations Tab
- Create agent configurations with JSON data
- Link configurations to templates
- Edit existing configurations
- Duplicate configurations

### Custom Agents Tab
- Define custom agent types
- Set capabilities and available tools
- Write system prompts
- Define configuration schemas (optional)
- View source format and import status for imported agents

### Import & Convert Tab
- **File Upload**: Drag and drop agent definition files (YAML, JSON, MD)
- **Upload History**: View all uploaded files with parsing results
- **Format Conversion**: Convert agent definitions between Claude, Roo, and Custom formats
- **Conversion History**: Track all format conversions
- **Template Creation**: Create templates from uploaded files or converted data
- **Agent Cards**: Generate and preview Microsoft discoverability agent cards

## API Endpoints

### Core Endpoints

#### Templates
- `GET /api/templates` - List all templates
- `GET /api/templates/<id>` - Get specific template
- `POST /api/templates` - Create new template
- `PUT /api/templates/<id>` - Update template
- `DELETE /api/templates/<id>` - Delete template

#### Configurations
- `GET /api/configurations` - List all configurations
- `GET /api/configurations/<id>` - Get specific configuration
- `POST /api/configurations` - Create new configuration
- `PUT /api/configurations/<id>` - Update configuration
- `DELETE /api/configurations/<id>` - Delete configuration

#### Custom Agents
- `GET /api/custom-agents` - List all custom agents
- `GET /api/custom-agents/<id>` - Get specific custom agent
- `POST /api/custom-agents` - Create new custom agent
- `PUT /api/custom-agents/<id>` - Update custom agent
- `DELETE /api/custom-agents/<id>` - Delete custom agent

### File Upload Endpoints

- `POST /api/files/upload` - Upload a single agent definition file
- `POST /api/files/upload/multiple` - Upload multiple agent definition files
- `GET /api/files` - List all file uploads (with optional filters)
- `GET /api/files/<id>` - Get details of a specific file upload
- `DELETE /api/files/<id>` - Delete a file upload record

### Format Conversion Endpoints

- `POST /api/convert` - Convert agent definition between formats
- `POST /api/convert/file` - Convert an uploaded file to a different format
- `GET /api/convert/history` - Get conversion history (with optional filters)
- `GET /api/convert/formats` - Get list of supported formats

### Template Creation from Upload Endpoints

- `POST /api/templates/from-upload` - Create a template from an uploaded file
- `POST /api/templates/from-data` - Create a template from parsed agent data

### Agent Card Endpoints

- `GET /api/agent-cards` - List all agent cards (with optional filters)
- `GET /api/agent-cards/<id>` - Get specific agent card
- `POST /api/agent-cards/generate` - Generate agent card from entity
- `POST /api/agent-cards/generate/batch` - Generate multiple agent cards
- `PUT /api/agent-cards/<id>` - Update existing agent card
- `DELETE /api/agent-cards/<id>` - Delete agent card
- `GET /api/agent-cards/<id>/export` - Export agent card in specified format
- `POST /api/agent-cards/<id>/validate` - Validate agent card

For detailed API documentation with request/response examples, see [API.md](API.md).

## Project Structure

```
agent-modes-db/
├── app.py              # Flask application and API endpoints
├── database.py         # Database models and operations
├── schema.sql          # Database schema
├── requirements.txt    # Python dependencies
├── migrations/         # Database migration scripts
│   ├── 001_add_file_upload_support.sql
│   ├── 002_add_format_conversions.sql
│   └── 003_add_agent_cards.sql
├── parsers/           # Format-specific parsers
│   ├── __init__.py
│   ├── claude.py
│   ├── roo.py
│   └── custom.py
├── serializers/       # Format-specific serializers
│   ├── __init__.py
│   ├── claude.py
│   ├── roo.py
│   └── custom.py
├── converters/        # Format conversion logic
│   ├── __init__.py
│   ├── ir.py         # Intermediate Representation
│   └── universal.py  # Universal Converter
├── generators/       # Agent card generation
│   ├── __init__.py
│   └── agent_card.py
├── utils/            # Utility functions
│   └── __init__.py
├── static/
│   ├── css/
│   │   └── style.css   # Custom styles
│   └── js/
│       └── app.js      # Frontend JavaScript
├── templates/
│   └── index.html      # Main GUI page
├── README.md
├── API.md             # API documentation
├── USER_GUIDE.md      # User guide
├── MIGRATION.md       # Migration guide
└── ARCHITECTURE.md    # Architecture documentation
```

## Technologies

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome 6

## Development

The database is automatically initialized with seed data on first run. The database file (`agents.db`) is created in the project root directory.

To reset the database, simply delete `agents.db` and restart the application.

### Applying Database Migrations

If you're upgrading from an earlier version, you may need to apply database migrations. See [MIGRATION.md](MIGRATION.md) for detailed instructions.

### Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Apply database migrations (if needed):
```bash
python -c "import database; database.apply_migrations()"
```

3. Run the development server:
```bash
python app.py
```

The server will start on `http://localhost:5000` with debug mode enabled.

## Documentation

- [API.md](API.md) - Complete API documentation with request/response examples
- [USER_GUIDE.md](USER_GUIDE.md) - User guide with step-by-step instructions
- [MIGRATION.md](MIGRATION.md) - Database migration guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture and design documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines

## License

MIT License - feel free to use this project for any purpose.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
