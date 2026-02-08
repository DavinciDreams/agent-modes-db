# Contributing to Agent Modes Database

Thank you for your interest in contributing to Agent Modes Database! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your environment (OS, Python version, browser)
- Any relevant error messages or screenshots

### Suggesting Enhancements

We welcome feature requests! Please create an issue with:
- A clear description of the feature
- Why this feature would be useful
- Any examples or mockups if applicable

### Pull Requests

1. **Fork the repository** and create your branch from `master`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

3. **Test your changes**
   - Ensure the server starts without errors
   - Test all CRUD operations
   - Verify the UI works correctly

4. **Commit your changes**
   - Write clear, descriptive commit messages
   - Reference any related issues

5. **Push to your fork** and submit a pull request
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Guidelines

### Code Style

**Python:**
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions
- Keep functions focused and concise
- Use type hints where appropriate

**JavaScript:**
- Use modern ES6+ syntax
- Use consistent naming (camelCase for variables/functions)
- Add comments for complex logic
- Keep functions small and focused
- Use async/await for asynchronous operations

**HTML/CSS:**
- Use semantic HTML5 elements
- Follow Bootstrap conventions
- Keep styles organized and reusable
- Ensure responsive design

### Project Structure

```
agent-modes-db/
├── app.py              # Flask routes and API endpoints
├── database.py         # Database operations (keep separate from app.py)
├── schema.sql          # Database schema definitions
├── requirements.txt     # Python dependencies
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
│   ├── css/           # Stylesheets
│   │   └── style.css   # Custom styles
│   └── js/            # Frontend JavaScript
│       └── app.js      # Frontend JavaScript
├── templates/
│   └── index.html      # Main GUI page
├── README.md
├── API.md
├── USER_GUIDE.md
├── MIGRATION.md
└── ARCHITECTURE.md
```

### Adding New Agent Formats

To add support for a new agent format:

1. **Create a parser:**
   - Add a new file in `parsers/` directory (e.g., `newformat.py`)
   - Implement the `Parser` interface with required methods:
     - `parse(content: str) -> dict`: Parse file content into normalized data
     - `validate(data: dict) -> tuple[bool, list[str]]`: Validate parsed data
   - Register the parser in `parsers/__init__.py`

2. **Create a serializer:**
   - Add a new file in `serializers/` directory (e.g., `newformat.py`)
   - Implement the `Serializer` interface with required methods:
     - `serialize(ir_data: dict) -> dict`: Convert IR data to format-specific data
   - Register the serializer in `serializers/__init__.py`

3. **Update the Universal Converter:**
   - Add the new format to `UniversalConverter.get_supported_formats()`
   - Add conversion logic in `UniversalConverter.convert()`
   - Add validation rules in `UniversalConverter.validate_conversion()`

4. **Add tests:**
   - Create test files for the new parser and serializer
   - Test format detection
   - Test conversion to/from the new format

5. **Update documentation:**
   - Add the new format to API.md
   - Update USER_GUIDE.md with format-specific instructions
   - Update ARCHITECTURE.md with format details

### Adding New Parsers

When adding a new parser:

1. **Inherit from base Parser class:**
   ```python
   from parsers.base import Parser
   
   class NewFormatParser(Parser):
       def parse(self, content: str) -> dict:
           # Parse content and return normalized data
           pass
       
       def validate(self, data: dict) -> tuple[bool, list[str]]:
           # Validate parsed data
           pass
   ```

2. **Implement required methods:**
   - `parse(content)`: Parse file content into normalized format
   - `validate(data)`: Validate parsed data against schema

3. **Handle errors gracefully:**
   - Raise `ValueError` with descriptive messages
   - Provide specific validation errors
   - Log errors for debugging

4. **Register in `parsers/__init__.py`:**
   ```python
   from parsers.newformat import NewFormatParser
   
   _parsers = {
       'newformat': NewFormatParser(),
       # ... other parsers
   }
   ```

### Adding New Serializers

When adding a new serializer:

1. **Inherit from base Serializer class:**
   ```python
   from serializers.base import Serializer
   
   class NewFormatSerializer(Serializer):
       def serialize(self, ir_data: dict) -> dict:
           # Convert IR data to format-specific data
           pass
   ```

2. **Implement required methods:**
   - `serialize(ir_data)`: Convert IR data to format-specific data

3. **Handle data transformation:**
   - Map IR fields to format-specific fields
   - Handle optional fields appropriately
   - Preserve data integrity

4. **Register in `serializers/__init__.py`:**
   ```python
   from serializers.newformat import NewFormatSerializer
   
   _serializers = {
       'newformat': NewFormatSerializer(),
       # ... other serializers
   }
   ```

### Database Changes

If you modify the database schema:

1. **Create a migration script:**
   - Add a new file in `migrations/` directory
   - Follow naming convention: `XXX_description.sql`
   - Use sequential numbering (001, 002, 003, ...)
   - Include both forward and rollback SQL

2. **Update `database.py`:**
   - Add new functions for the new tables/columns
   - Follow existing naming conventions
   - Include proper error handling
   - Update `init_db()` if needed

3. **Update `schema.sql`:**
   - Add new table definitions
   - Keep schema.sql in sync with migrations
   - Document any schema changes

4. **Document migration steps:**
   - Update MIGRATION.md with instructions
   - Include rollback procedures
   - Note any breaking changes

5. **Consider backward compatibility:**
   - Provide migration paths for existing data
   - Avoid breaking existing functionality
   - Test with existing databases

### API Changes

If you add or modify API endpoints:

1. **Update the API documentation:**
   - Add new endpoints to API.md
   - Include request/response examples
   - Document error responses
   - Update endpoint lists in README.md

2. **Follow RESTful conventions:**
   - Use appropriate HTTP methods (GET, POST, PUT, DELETE)
   - Use resource-based URLs
   - Return appropriate status codes
   - Include proper error handling

3. **Include proper error handling:**
   - Validate input data
   - Return descriptive error messages
   - Use appropriate HTTP status codes
   - Log errors for debugging

4. **Return appropriate HTTP status codes:**
   - `200 OK` - Request successful
   - `201 Created` - Resource created
   - `400 Bad Request` - Invalid request
   - `403 Forbidden` - Operation not allowed
   - `404 Not Found` - Resource not found
   - `500 Internal Server Error` - Server error

### UI Changes

If you modify the user interface:

1. **Ensure responsive design:**
   - Test on mobile, tablet, and desktop
   - Use Bootstrap's responsive classes
   - Test with different screen sizes
   - Ensure touch targets are accessible

2. **Maintain consistent styling:**
   - Follow existing design patterns
   - Use Bootstrap components appropriately
   - Keep color scheme consistent
   - Use existing CSS classes where possible

3. **Add appropriate loading states:**
   - Show loading indicators during async operations
   - Disable buttons during processing
   - Provide user feedback
   - Handle timeouts gracefully

4. **Include user feedback:**
   - Show toast notifications for success/error
   - Confirm destructive actions
   - Provide clear error messages
   - Guide users through workflows

5. **Test across browsers:**
   - Test in Chrome, Firefox, Safari, and Edge
   - Check for browser-specific issues
   - Use standard JavaScript APIs
   - Provide fallbacks for unsupported features

### Database Changes

If you modify the database schema:
1. Update `schema.sql`
2. Update the relevant functions in `database.py`
3. Document migration steps in your PR
4. Consider backward compatibility

### API Changes

If you add or modify API endpoints:
1. Update the API documentation in README.md
2. Follow RESTful conventions
3. Include proper error handling
4. Return appropriate HTTP status codes

### UI Changes

If you modify the user interface:
1. Ensure responsive design (test on mobile/tablet)
2. Maintain consistent styling with existing UI
3. Add appropriate loading states
4. Include user feedback (toasts, confirmations)

## Testing

Before submitting a PR, please test:

1. **Backend:**
   - Start the server: `python app.py`
   - Test all API endpoints
   - Check for Python errors
   - Test file upload functionality
   - Test format conversion logic
   - Test agent card generation

2. **Frontend:**
   - Test all CRUD operations through the UI
   - Test in multiple browsers (Chrome, Firefox, Safari)
   - Check responsive design
   - Verify form validation
   - Test drag and drop functionality
   - Test modal interactions

3. **Integration:**
   - Test complete workflows (create → edit → delete)
   - Verify data persistence
   - Check error handling
   - Test file upload → conversion → template creation workflow
   - Test agent card generation → validation → export workflow

4. **File Upload Testing:**
   - Test uploading single files (YAML, JSON, MD)
   - Test uploading multiple files
   - Test with invalid file formats
   - Test with corrupted files
   - Test with large files
   - Verify parsing results

5. **Format Conversion Testing:**
   - Test conversions between all supported formats
   - Test with incomplete data
   - Test with format-specific features
   - Verify conversion warnings
   - Check conversion history

6. **Agent Card Testing:**
   - Test card generation from all entity types
   - Test card validation
   - Test card export (JSON and YAML)
   - Test batch card generation
   - Verify card schema compliance

### Testing Guidelines

**Unit Tests:**
- Write unit tests for new functions
- Test edge cases and error conditions
- Mock external dependencies
- Aim for high code coverage

**Integration Tests:**
- Test complete user workflows
- Test API endpoints end-to-end
- Verify database operations
- Test file upload and processing

**Frontend Tests:**
- Test UI interactions
- Verify responsive behavior
- Test form validation
- Check error handling
- Test across browsers

**Performance Tests:**
- Test with large files
- Test with multiple concurrent uploads
- Monitor memory usage
- Check response times

## Feature Ideas

Here are some ideas if you're looking for something to work on:

- **Export/Import**: JSON export/import for agents and configurations
- **Search**: Full-text search across agents and templates
- **Versioning**: Track changes to agent definitions over time
- **Testing**: Add unit tests for backend and frontend
- **API Documentation**: Auto-generated API docs (Swagger/OpenAPI)
- **Agent Execution**: Actually run agents and track results
- **Multi-user**: Add authentication and user management
- **Agent Sharing**: Share agent templates with the community
- **Dark Mode**: Add theme toggle
- **Code Highlighting**: Syntax highlighting for JSON and prompts

## Questions?

If you have questions about contributing, feel free to:
- Open an issue for discussion
- Reach out to the maintainers

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

Thank you for contributing! 🚀
