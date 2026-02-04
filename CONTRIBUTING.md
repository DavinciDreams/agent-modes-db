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

**JavaScript:**
- Use modern ES6+ syntax
- Use consistent naming (camelCase for variables/functions)
- Add comments for complex logic
- Keep functions small and focused

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
├── static/
│   ├── css/           # Stylesheets
│   └── js/            # Frontend JavaScript
└── templates/         # HTML templates
```

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

2. **Frontend:**
   - Test all CRUD operations through the UI
   - Test in multiple browsers (Chrome, Firefox, Safari)
   - Check responsive design
   - Verify form validation

3. **Integration:**
   - Test complete workflows (create → edit → delete)
   - Verify data persistence
   - Check error handling

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
