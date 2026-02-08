# Agent Modes Database - User Guide

Complete user guide for the Agent Modes Database & GUI application.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Managing Templates](#managing-templates)
3. [Managing Configurations](#managing-configurations)
4. [Managing Custom Agents](#managing-custom-agents)
5. [File Upload](#file-upload)
6. [Format Conversion](#format-conversion)
7. [Creating Templates from Uploads](#creating-templates-from-uploads)
8. [Agent Card Generation](#agent-card-generation)
9. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/agent-modes-db.git
   cd agent-modes-db
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the application:**
   ```bash
   python app.py
   ```

5. **Open your browser:**
   Navigate to `http://localhost:5000`

### Interface Overview

The application consists of four main tabs:

1. **Templates** - Manage agent templates
2. **Configurations** - Create and edit agent configurations
3. **Custom Agents** - Define custom agent types
4. **Import & Convert** - Upload files, convert formats, and generate agent cards

---

## Managing Templates

### Viewing Templates

1. Click on the **Templates** tab
2. You'll see a grid of available templates
3. Each template card displays:
   - Template name
   - Description
   - Category badge
   - Built-in badge (for system templates)
   - Action buttons (Edit/Delete for custom templates)

### Filtering Templates

1. Use the **Category Filter** dropdown at the top of the Templates tab
2. Select a category to filter templates
3. Select "All Categories" to show all templates

### Creating a New Template

1. Click the **Create Template** button
2. Fill in the form:
   - **Name**: A descriptive name for your template
   - **Description**: What this template does
   - **Category**: Choose or enter a category
3. Click **Save Template**
4. The template will appear in the templates grid

### Editing a Template

1. Click the **Edit** button on a custom template card
2. Modify the template details
3. Click **Save Template**
4. Changes are saved immediately

**Note:** Built-in templates cannot be edited.

### Deleting a Template

1. Click the **Delete** button on a custom template card
2. Confirm the deletion in the modal dialog
3. The template is permanently removed

**Note:** Built-in templates cannot be deleted.

---

## Managing Configurations

### Viewing Configurations

1. Click on the **Configurations** tab
2. You'll see a list of all configurations
3. Each configuration displays:
   - Configuration name
   - Associated template (if any)
   - JSON configuration data
   - Creation and update timestamps
   - Action buttons

### Creating a New Configuration

1. Click the **Create Configuration** button
2. Fill in the form:
   - **Name**: A descriptive name for your configuration
   - **Template**: Select an optional template to associate with
   - **Configuration JSON**: Enter or paste JSON configuration data
3. Click **Save Configuration**
4. The configuration will appear in the list

### Editing a Configuration

1. Click the **Edit** button on a configuration
2. Modify the configuration details
3. Click **Save Configuration**
4. Changes are saved immediately

### Duplicating a Configuration

1. Click the **Duplicate** button on a configuration
2. A copy of the configuration will be created with a new ID
3. You can then edit the duplicate as needed

### Deleting a Configuration

1. Click the **Delete** button on a configuration
2. Confirm the deletion in the modal dialog
3. The configuration is permanently removed

---

## Managing Custom Agents

### Viewing Custom Agents

1. Click on the **Custom Agents** tab
2. You'll see a list of all custom agents
3. Each agent displays:
   - Agent name
   - Description
   - Capabilities (as badges)
   - Tools (as badges)
   - System prompt preview
   - Action buttons

### Creating a New Custom Agent

1. Click the **Create Custom Agent** button
2. Fill in the form:
   - **Name**: A descriptive name for your agent
   - **Description**: What this agent does
   - **Capabilities**: Enter capabilities as a JSON array (e.g., `["code_analysis", "debugging"]`)
   - **Tools**: Enter available tools as a JSON array (e.g., `["file_reader", "code_executor"]`)
   - **System Prompt**: The system prompt that defines the agent's behavior
   - **Configuration Schema** (optional): JSON schema for configuration validation
3. Click **Save Custom Agent**
4. The agent will appear in the list

### Editing a Custom Agent

1. Click the **Edit** button on a custom agent
2. Modify the agent details
3. Click **Save Custom Agent**
4. Changes are saved immediately

### Deleting a Custom Agent

1. Click the **Delete** button on a custom agent
2. Confirm the deletion in the modal dialog
3. The agent is permanently removed

---

## File Upload

### Using Drag and Drop

The Import & Convert tab provides an intuitive drag and drop interface for uploading agent definition files.

#### Uploading a Single File

1. Navigate to the **Import & Convert** tab
2. You'll see a drag and drop zone with the text "Drop agent definition files here"
3. Drag a file from your computer and drop it into the zone
4. Alternatively, click the zone to open a file picker
5. The file will be automatically uploaded and parsed
6. You'll see a success notification when the upload is complete

#### Supported File Formats

- **YAML files** (.yaml, .yml)
- **JSON files** (.json)
- **Markdown files** (.md)

#### Uploading Multiple Files

1. Navigate to the **Import & Convert** tab
2. Drag multiple files and drop them into the zone
3. Alternatively, click the zone and select multiple files
4. All files will be uploaded simultaneously
5. You'll see a summary of successful and failed uploads

### Viewing Upload History

1. Navigate to the **Import & Convert** tab
2. Scroll down to the **Recent Uploads** section
3. You'll see a list of all uploaded files with:
   - Original filename
   - File format
   - Upload status (completed/failed)
   - Upload timestamp
   - Action buttons (View, Create Template, Delete)

### Viewing Upload Details

1. Click the **View** button on an upload in the history
2. A modal will appear showing:
   - File metadata (name, format, size)
   - Parsed data (if upload was successful)
   - Error message (if upload failed)

### Deleting Uploads

1. Click the **Delete** button on an upload in the history
2. Confirm the deletion
3. The upload record is removed from the database

**Note:** Deleting an upload does not affect any templates or agents created from it.

---

## Format Conversion

### Converting Agent Definitions

The application supports converting agent definitions between different formats:

- **Claude format** - Anthropic Claude agent definitions
- **Roo format** - Roo Code agent definitions
- **Custom format** - Generic custom agent definitions

### Converting an Uploaded File

1. Upload a file using the drag and drop zone (see [File Upload](#file-upload))
2. Once uploaded, click the **Convert** button on the upload in the history
3. A modal will appear:
   - Select the **Target Format** from the dropdown
   - The source format is auto-detected
4. Click **Convert**
5. The converted data will be displayed
6. You can copy the converted data or create a template from it

### Converting with Direct Data

1. Navigate to the **Import & Convert** tab
2. Scroll to the **Format Converter** section
3. Enter or paste your agent data in JSON format
4. Select the **Source Format** and **Target Format**
5. Click **Convert**
6. The converted data will be displayed
7. You can copy the result or create a template from it

### Viewing Conversion History

1. Navigate to the **Import & Convert** tab
2. Scroll down to the **Recent Conversions** section
3. You'll see a list of all conversions with:
   - Source format → Target format
   - Conversion status
   - Timestamp
   - Action buttons (View, Delete)

### Understanding Conversion Warnings

Some conversions may generate warnings when:

- Data is not perfectly compatible between formats
- Optional fields are missing
- Format-specific features cannot be preserved

Review warnings carefully to ensure the converted data meets your needs.

---

## Creating Templates from Uploads

### Creating a Template from an Uploaded File

1. Upload a file using the drag and drop zone
2. Click the **Create Template** button on the upload in the history
3. A modal will appear with pre-filled data from the upload:
   - **Name**: Auto-filled from the uploaded data (editable)
   - **Description**: Auto-filled from the uploaded data (editable)
   - **Category**: Enter a category for the template
4. Optionally, edit the data fields
5. Click **Create Template**
6. The template is created and linked to the upload

### Creating a Template from Converted Data

1. Convert an agent definition (see [Format Conversion](#format-conversion))
2. After conversion, click **Create Template from Converted Data**
3. Fill in the template details
4. Click **Create Template**
5. The template is created with the converted data

### Viewing Imported Templates

Imported templates appear in the Templates tab with:
- **Source Format** badge (e.g., "Claude", "Roo", "Custom")
- **Imported** badge
- Link to the original upload (if applicable)

---

## Agent Card Generation

### What are Agent Cards?

Agent Cards are standardized, discoverable metadata files that describe agents for the Microsoft ecosystem. They follow Microsoft's agent card schema and can be exported for use in Microsoft's agent discovery system.

### Generating an Agent Card

#### From a Template

1. Navigate to the **Templates** tab
2. Find the template you want to generate a card for
3. Click the **Generate Agent Card** button
4. A modal will appear with the generated card data
5. Review the card data
6. Click **Save Card**

#### From a Configuration

1. Navigate to the **Configurations** tab
2. Find the configuration you want to generate a card for
3. Click the **Generate Agent Card** button
4. A modal will appear with the generated card data
5. Review the card data
6. Click **Save Card**

#### From a Custom Agent

1. Navigate to the **Custom Agents** tab
2. Find the custom agent you want to generate a card for
3. Click the **Generate Agent Card** button
4. A modal will appear with the generated card data
5. Review the card data
6. Click **Save Card**

### Viewing Agent Cards

1. Navigate to the **Import & Convert** tab
2. Scroll to the **Agent Cards** section
3. You'll see a list of all generated cards with:
   - Card name
   - Entity type (template/configuration/custom_agent)
   - Published status
   - Generation timestamp
   - Action buttons (View, Export, Validate, Delete)

### Previewing Agent Cards

1. Click the **View** button on an agent card
2. A modal will appear showing the complete card data
3. The card is displayed in a formatted, readable view

### Exporting Agent Cards

1. Click the **Export** button on an agent card
2. Select the export format (JSON or YAML)
3. The card data will be downloaded as a file
4. The filename follows the pattern: `agent-card-{id}.{format}`

### Validating Agent Cards

1. Click the **Validate** button on an agent card
2. The system will check if the card meets Microsoft's agent card schema
3. A modal will appear showing:
   - Validation status (Valid/Invalid)
   - Any validation errors or warnings

### Publishing Agent Cards

1. Click the **View** button on an agent card
2. Toggle the **Published** switch
3. Click **Update Card**
4. The card's published status is updated

**Note:** Publishing a card marks it as ready for discovery but does not automatically publish it to any external system.

### Batch Generating Agent Cards

1. Navigate to the **Import & Convert** tab
2. Scroll to the **Agent Cards** section
3. Click the **Batch Generate** button
4. Select the entities you want to generate cards for:
   - All templates
   - All configurations
   - All custom agents
   - Or select specific entities
5. Click **Generate Cards**
6. Cards will be generated for all selected entities
7. You'll see a summary of successful and failed generations

---

## Troubleshooting

### File Upload Issues

**Problem:** File upload fails with "Invalid file format" error

**Solution:**
- Ensure the file extension is .yaml, .yml, .json, or .md
- Check that the file contains valid YAML, JSON, or Markdown
- Verify the file is not corrupted

**Problem:** File upload fails with "Validation failed" error

**Solution:**
- Review the error message for specific validation issues
- Ensure the file contains all required fields for the agent format
- Check that field values are in the correct format

**Problem:** File upload fails with "File encoding error"

**Solution:**
- Ensure the file uses UTF-8 encoding
- Re-save the file with UTF-8 encoding
- Avoid special characters that may cause encoding issues

### Format Conversion Issues

**Problem:** Conversion fails with "Invalid conversion" error

**Solution:**
- Verify both source and target formats are supported (claude, roo, custom)
- Check that the source data is valid for the specified source format
- Review the error message for specific conversion issues

**Problem:** Conversion succeeds but shows warnings

**Solution:**
- Review the warnings carefully
- Some warnings may indicate data loss or incompatibility
- Manually edit the converted data if needed

**Problem:** Converted data is missing information

**Solution:**
- Some formats have different field structures
- Not all fields can be perfectly converted between formats
- Manually add missing information after conversion

### Agent Card Generation Issues

**Problem:** Agent card generation fails

**Solution:**
- Ensure the entity (template/configuration/custom_agent) exists
- Check that the entity has all required fields
- Review the error message for specific issues

**Problem:** Agent card validation fails

**Solution:**
- Review the validation errors
- Ensure all required fields are present
- Check that field values meet the schema requirements
- Update the card data and re-validate

**Problem:** Exported card file is empty or corrupted

**Solution:**
- Ensure the card data is valid before exporting
- Try exporting in a different format (JSON or YAML)
- Check your browser's download settings

### General Issues

**Problem:** Changes are not saved

**Solution:**
- Check your internet connection (if applicable)
- Look for error messages in the UI
- Try refreshing the page and retrying
- Check the browser console for JavaScript errors

**Problem:** Page loads slowly or times out

**Solution:**
- Check your internet connection
- Clear your browser cache
- Try a different browser
- Check if the server is running (`python app.py`)

**Problem:** Data is missing after page refresh

**Solution:**
- This is normal behavior - data is stored in the database
- Refreshing the page reloads data from the database
- If data is truly missing, check the database file

**Problem:** Cannot delete built-in templates

**Solution:**
- This is intentional - built-in templates are protected
- You can create custom templates instead
- Copy the built-in template data to create a custom version

### Getting Help

If you encounter issues not covered in this guide:

1. Check the [API Documentation](API.md) for technical details
2. Review the [Architecture Documentation](ARCHITECTURE.md) for system design
3. Check the [Migration Guide](MIGRATION.md) for database issues
4. Open an issue on GitHub with:
   - A clear description of the problem
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Your environment (OS, Python version, browser)
   - Any error messages or screenshots

---

## Best Practices

### File Upload

- Always validate files before uploading
- Use descriptive filenames for easy identification
- Keep backup copies of important files
- Review parsed data after upload

### Format Conversion

- Understand the differences between formats before converting
- Review conversion warnings carefully
- Test converted data before using it in production
- Keep original files as backups

### Template Creation

- Use clear, descriptive names
- Provide detailed descriptions
- Organize templates into logical categories
- Regularly review and update templates

### Agent Card Generation

- Generate cards for all important agents
- Validate cards before publishing
- Keep card data up to date
- Export cards for backup and sharing

---

## Keyboard Shortcuts

The application supports the following keyboard shortcuts:

- **Ctrl/Cmd + S** - Save current form (when editing)
- **Escape** - Close modal dialogs
- **Enter** - Submit form (when in a modal)

---

## Tips and Tricks

1. **Batch Operations:** Use the batch upload and batch card generation features to save time when working with multiple files or agents.

2. **Format Detection:** The system automatically detects file formats, so you don't need to specify them manually.

3. **Template Reuse:** Create templates from successful conversions to reuse agent definitions across different formats.

4. **Card Validation:** Always validate agent cards before publishing to ensure they meet Microsoft's requirements.

5. **Data Backup:** Regularly export agent cards and configurations to create backups of your important data.

6. **Category Organization:** Use categories effectively to organize templates and make them easier to find.

7. **Search Functionality:** Use the browser's find function (Ctrl/Cmd + F) to quickly locate specific items in lists.

---

## Additional Resources

- [API Documentation](API.md) - Complete API reference
- [Architecture Documentation](ARCHITECTURE.md) - System design and architecture
- [Migration Guide](MIGRATION.md) - Database migration instructions
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the project
- [README](README.md) - Project overview and quick start

---

## Version History

- **v1.0** - Initial release with core features
- **v1.1** - Added file upload and parsing
- **v1.2** - Added format conversion
- **v1.3** - Added agent card generation
- **v1.4** - Enhanced UI with drag and drop

---

## Support

For additional support:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the documentation thoroughly
- Contact the maintainers for critical issues
