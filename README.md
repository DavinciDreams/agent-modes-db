# Agent Modes Database & GUI

A web-based management system for agent configurations, templates, and custom agent definitions. Built with Flask and vanilla JavaScript.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

## Features

- **Agent Templates**: Browse and manage pre-built agent templates
- **Configurations**: Create and edit agent configurations with JSON editor
- **Custom Agents**: Define your own agent types with capabilities, tools, and system prompts
- **REST API**: Full CRUD operations via RESTful API
- **Modern UI**: Responsive interface with Bootstrap 5
- **SQLite Database**: Lightweight, file-based storage

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
pip install Flask
```

### Running the Application

Start the server:
```bash
python app.py
```

Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Templates Tab
- View 5 built-in agent templates (Code Explorer, Test Runner, Documentation Generator, Bug Fixer, Code Reviewer)
- Create custom templates
- Filter by category
- Edit and delete custom templates (built-in templates are protected)

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

## API Endpoints

### Templates
- `GET /api/templates` - List all templates
- `GET /api/templates/<id>` - Get specific template
- `POST /api/templates` - Create new template
- `PUT /api/templates/<id>` - Update template
- `DELETE /api/templates/<id>` - Delete template

### Configurations
- `GET /api/configurations` - List all configurations
- `GET /api/configurations/<id>` - Get specific configuration
- `POST /api/configurations` - Create new configuration
- `PUT /api/configurations/<id>` - Update configuration
- `DELETE /api/configurations/<id>` - Delete configuration

### Custom Agents
- `GET /api/custom-agents` - List all custom agents
- `GET /api/custom-agents/<id>` - Get specific custom agent
- `POST /api/custom-agents` - Create new custom agent
- `PUT /api/custom-agents/<id>` - Update custom agent
- `DELETE /api/custom-agents/<id>` - Delete custom agent

## Project Structure

```
agent-modes-db/
├── app.py              # Flask application and API endpoints
├── database.py         # Database models and operations
├── schema.sql          # Database schema
├── static/
│   ├── css/
│   │   └── style.css   # Custom styles
│   └── js/
│       └── app.js      # Frontend JavaScript
├── templates/
│   └── index.html      # Main GUI page
└── README.md
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

## License

MIT License - feel free to use this project for any purpose.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
