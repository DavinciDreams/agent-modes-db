// Global state
let templates = [];
let configurations = [];
let customAgents = [];
let currentDeleteCallback = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadTemplates();
    loadConfigurations();
    loadCustomAgents();

    // Set up tab change listeners
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', (e) => {
            const target = e.target.getAttribute('data-bs-target');
            if (target === '#templates') loadTemplates();
            else if (target === '#configurations') loadConfigurations();
            else if (target === '#custom-agents') loadCustomAgents();
        });
    });
});

// ============================================
// Utility Functions
// ============================================

function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    const toastId = 'toast-' + Date.now();

    const bgClass = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-info';

    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// ============================================
// Templates Functions
// ============================================

async function loadTemplates() {
    try {
        const response = await fetch('/api/templates');
        templates = await response.json();

        // Update category filter
        const categories = [...new Set(templates.map(t => t.category))];
        const filterSelect = document.getElementById('categoryFilter');
        const currentValue = filterSelect.value;
        filterSelect.innerHTML = '<option value="">All Categories</option>';
        categories.forEach(cat => {
            filterSelect.innerHTML += `<option value="${cat}">${cat}</option>`;
        });
        filterSelect.value = currentValue;

        renderTemplates();
    } catch (error) {
        showToast('Error loading templates: ' + error.message, 'error');
    }
}

function filterTemplates() {
    renderTemplates();
}

function renderTemplates() {
    const grid = document.getElementById('templatesGrid');
    const filter = document.getElementById('categoryFilter').value;

    const filtered = filter ? templates.filter(t => t.category === filter) : templates;

    if (filtered.length === 0) {
        grid.innerHTML = '<div class="col-12"><p class="text-muted">No templates found</p></div>';
        return;
    }

    grid.innerHTML = filtered.map(template => `
        <div class="col-md-4">
            <div class="card h-100 ${template.is_builtin ? 'border-primary' : ''}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h5 class="card-title mb-0">${template.name}</h5>
                        ${template.is_builtin ? '<span class="badge bg-primary">Built-in</span>' : ''}
                    </div>
                    <p class="card-text text-muted small mb-2">${template.description}</p>
                    <div class="mb-3">
                        <span class="badge bg-secondary">${template.category}</span>
                    </div>
                    <div class="btn-group w-100" role="group">
                        ${!template.is_builtin ? `
                            <button class="btn btn-sm btn-outline-primary" onclick="editTemplate(${template.id})">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="confirmDeleteTemplate(${template.id})">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        ` : '<button class="btn btn-sm btn-outline-secondary" disabled>System Template</button>'}
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function showCreateTemplateModal() {
    document.getElementById('templateModalTitle').textContent = 'Create Template';
    document.getElementById('templateForm').reset();
    document.getElementById('templateId').value = '';
    new bootstrap.Modal(document.getElementById('templateModal')).show();
}

function editTemplate(id) {
    const template = templates.find(t => t.id === id);
    if (!template) return;

    document.getElementById('templateModalTitle').textContent = 'Edit Template';
    document.getElementById('templateId').value = template.id;
    document.getElementById('templateName').value = template.name;
    document.getElementById('templateDescription').value = template.description;
    document.getElementById('templateCategory').value = template.category;

    new bootstrap.Modal(document.getElementById('templateModal')).show();
}

async function saveTemplate() {
    const id = document.getElementById('templateId').value;
    const data = {
        name: document.getElementById('templateName').value,
        description: document.getElementById('templateDescription').value,
        category: document.getElementById('templateCategory').value
    };

    try {
        const url = id ? `/api/templates/${id}` : '/api/templates';
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save template');
        }

        showToast(id ? 'Template updated successfully' : 'Template created successfully');
        bootstrap.Modal.getInstance(document.getElementById('templateModal')).hide();
        loadTemplates();
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
}

function confirmDeleteTemplate(id) {
    const template = templates.find(t => t.id === id);
    document.getElementById('deleteConfirmText').textContent =
        `Are you sure you want to delete the template "${template.name}"?`;

    currentDeleteCallback = () => deleteTemplate(id);
    document.getElementById('confirmDeleteBtn').onclick = currentDeleteCallback;

    new bootstrap.Modal(document.getElementById('confirmDeleteModal')).show();
}

async function deleteTemplate(id) {
    try {
        const response = await fetch(`/api/templates/${id}`, { method: 'DELETE' });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to delete template');
        }

        showToast('Template deleted successfully');
        bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal')).hide();
        loadTemplates();
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
}

// ============================================
// Configurations Functions
// ============================================

async function loadConfigurations() {
    try {
        const response = await fetch('/api/configurations');
        configurations = await response.json();
        renderConfigurations();
    } catch (error) {
        showToast('Error loading configurations: ' + error.message, 'error');
    }
}

function renderConfigurations() {
    const tbody = document.querySelector('#configurationsTable tbody');

    if (configurations.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-muted text-center">No configurations found</td></tr>';
        return;
    }

    tbody.innerHTML = configurations.map(config => `
        <tr>
            <td>${config.name}</td>
            <td>${config.template_name || '<em class="text-muted">None</em>'}</td>
            <td>${formatDate(config.updated_at)}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="editConfiguration(${config.id})">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button class="btn btn-sm btn-outline-info" onclick="duplicateConfiguration(${config.id})">
                    <i class="fas fa-copy"></i> Duplicate
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="confirmDeleteConfiguration(${config.id})">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </td>
        </tr>
    `).join('');
}

async function showCreateConfigurationModal() {
    // Load templates for dropdown
    if (templates.length === 0) await loadTemplates();

    const select = document.getElementById('configurationTemplate');
    select.innerHTML = '<option value="">None</option>';
    templates.forEach(t => {
        select.innerHTML += `<option value="${t.id}">${t.name}</option>`;
    });

    document.getElementById('configurationModalTitle').textContent = 'Create Configuration';
    document.getElementById('configurationForm').reset();
    document.getElementById('configurationId').value = '';
    document.getElementById('configurationJson').value = '{\n  "key": "value"\n}';

    new bootstrap.Modal(document.getElementById('configurationModal')).show();
}

async function editConfiguration(id) {
    const config = configurations.find(c => c.id === id);
    if (!config) return;

    // Load templates for dropdown
    if (templates.length === 0) await loadTemplates();

    const select = document.getElementById('configurationTemplate');
    select.innerHTML = '<option value="">None</option>';
    templates.forEach(t => {
        select.innerHTML += `<option value="${t.id}">${t.name}</option>`;
    });

    document.getElementById('configurationModalTitle').textContent = 'Edit Configuration';
    document.getElementById('configurationId').value = config.id;
    document.getElementById('configurationName').value = config.name;
    document.getElementById('configurationTemplate').value = config.template_id || '';

    // Pretty print JSON
    try {
        const jsonObj = JSON.parse(config.config_json);
        document.getElementById('configurationJson').value = JSON.stringify(jsonObj, null, 2);
    } catch {
        document.getElementById('configurationJson').value = config.config_json;
    }

    new bootstrap.Modal(document.getElementById('configurationModal')).show();
}

async function duplicateConfiguration(id) {
    const config = configurations.find(c => c.id === id);
    if (!config) return;

    // Load templates for dropdown
    if (templates.length === 0) await loadTemplates();

    const select = document.getElementById('configurationTemplate');
    select.innerHTML = '<option value="">None</option>';
    templates.forEach(t => {
        select.innerHTML += `<option value="${t.id}">${t.name}</option>`;
    });

    document.getElementById('configurationModalTitle').textContent = 'Duplicate Configuration';
    document.getElementById('configurationId').value = '';
    document.getElementById('configurationName').value = config.name + ' (Copy)';
    document.getElementById('configurationTemplate').value = config.template_id || '';

    // Pretty print JSON
    try {
        const jsonObj = JSON.parse(config.config_json);
        document.getElementById('configurationJson').value = JSON.stringify(jsonObj, null, 2);
    } catch {
        document.getElementById('configurationJson').value = config.config_json;
    }

    new bootstrap.Modal(document.getElementById('configurationModal')).show();
}

async function saveConfiguration() {
    const id = document.getElementById('configurationId').value;
    const jsonText = document.getElementById('configurationJson').value;

    // Validate JSON
    try {
        JSON.parse(jsonText);
    } catch (e) {
        showToast('Invalid JSON: ' + e.message, 'error');
        return;
    }

    const templateId = document.getElementById('configurationTemplate').value;
    const data = {
        name: document.getElementById('configurationName').value,
        template_id: templateId ? parseInt(templateId) : null,
        config_json: jsonText
    };

    try {
        const url = id ? `/api/configurations/${id}` : '/api/configurations';
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save configuration');
        }

        showToast(id ? 'Configuration updated successfully' : 'Configuration created successfully');
        bootstrap.Modal.getInstance(document.getElementById('configurationModal')).hide();
        loadConfigurations();
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
}

function confirmDeleteConfiguration(id) {
    const config = configurations.find(c => c.id === id);
    document.getElementById('deleteConfirmText').textContent =
        `Are you sure you want to delete the configuration "${config.name}"?`;

    currentDeleteCallback = () => deleteConfiguration(id);
    document.getElementById('confirmDeleteBtn').onclick = currentDeleteCallback;

    new bootstrap.Modal(document.getElementById('confirmDeleteModal')).show();
}

async function deleteConfiguration(id) {
    try {
        const response = await fetch(`/api/configurations/${id}`, { method: 'DELETE' });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to delete configuration');
        }

        showToast('Configuration deleted successfully');
        bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal')).hide();
        loadConfigurations();
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
}

// ============================================
// Custom Agents Functions
// ============================================

async function loadCustomAgents() {
    try {
        const response = await fetch('/api/custom-agents');
        customAgents = await response.json();
        renderCustomAgents();
    } catch (error) {
        showToast('Error loading custom agents: ' + error.message, 'error');
    }
}

function renderCustomAgents() {
    const grid = document.getElementById('customAgentsGrid');

    if (customAgents.length === 0) {
        grid.innerHTML = '<div class="col-12"><p class="text-muted">No custom agents found</p></div>';
        return;
    }

    grid.innerHTML = customAgents.map(agent => {
        let capabilities = [];
        let tools = [];

        try {
            capabilities = JSON.parse(agent.capabilities);
            tools = JSON.parse(agent.tools);
        } catch (e) {
            // Ignore parse errors
        }

        return `
            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">${agent.name}</h5>
                        <p class="card-text text-muted small">${agent.description}</p>
                        <div class="mb-2">
                            <strong>Capabilities:</strong>
                            <div class="mt-1">
                                ${capabilities.map(c => `<span class="badge bg-info me-1">${c}</span>`).join('')}
                            </div>
                        </div>
                        <div class="mb-3">
                            <strong>Tools:</strong>
                            <div class="mt-1">
                                ${tools.map(t => `<span class="badge bg-secondary me-1">${t}</span>`).join('')}
                            </div>
                        </div>
                        <div class="btn-group w-100" role="group">
                            <button class="btn btn-sm btn-outline-primary" onclick="editCustomAgent(${agent.id})">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            <button class="btn btn-sm btn-outline-info" onclick="cloneCustomAgent(${agent.id})">
                                <i class="fas fa-clone"></i> Clone
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="confirmDeleteCustomAgent(${agent.id})">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function showCreateCustomAgentModal() {
    document.getElementById('customAgentModalTitle').textContent = 'Create Custom Agent';
    document.getElementById('customAgentForm').reset();
    document.getElementById('customAgentId').value = '';
    document.getElementById('customAgentPrompt').value = 'You are a specialized agent designed to...';
    new bootstrap.Modal(document.getElementById('customAgentModal')).show();
}

function editCustomAgent(id) {
    const agent = customAgents.find(a => a.id === id);
    if (!agent) return;

    document.getElementById('customAgentModalTitle').textContent = 'Edit Custom Agent';
    document.getElementById('customAgentId').value = agent.id;
    document.getElementById('customAgentName').value = agent.name;
    document.getElementById('customAgentDescription').value = agent.description;
    document.getElementById('customAgentPrompt').value = agent.system_prompt;

    // Parse arrays to comma-separated
    try {
        const capabilities = JSON.parse(agent.capabilities);
        document.getElementById('customAgentCapabilities').value = capabilities.join(', ');
    } catch {
        document.getElementById('customAgentCapabilities').value = agent.capabilities;
    }

    try {
        const tools = JSON.parse(agent.tools);
        document.getElementById('customAgentTools').value = tools.join(', ');
    } catch {
        document.getElementById('customAgentTools').value = agent.tools;
    }

    // Pretty print schema
    if (agent.config_schema) {
        try {
            const schema = JSON.parse(agent.config_schema);
            document.getElementById('customAgentSchema').value = JSON.stringify(schema, null, 2);
        } catch {
            document.getElementById('customAgentSchema').value = agent.config_schema;
        }
    } else {
        document.getElementById('customAgentSchema').value = '';
    }

    new bootstrap.Modal(document.getElementById('customAgentModal')).show();
}

function cloneCustomAgent(id) {
    const agent = customAgents.find(a => a.id === id);
    if (!agent) return;

    document.getElementById('customAgentModalTitle').textContent = 'Clone Custom Agent';
    document.getElementById('customAgentId').value = '';
    document.getElementById('customAgentName').value = agent.name + ' (Copy)';
    document.getElementById('customAgentDescription').value = agent.description;
    document.getElementById('customAgentPrompt').value = agent.system_prompt;

    // Parse arrays to comma-separated
    try {
        const capabilities = JSON.parse(agent.capabilities);
        document.getElementById('customAgentCapabilities').value = capabilities.join(', ');
    } catch {
        document.getElementById('customAgentCapabilities').value = agent.capabilities;
    }

    try {
        const tools = JSON.parse(agent.tools);
        document.getElementById('customAgentTools').value = tools.join(', ');
    } catch {
        document.getElementById('customAgentTools').value = agent.tools;
    }

    // Pretty print schema
    if (agent.config_schema) {
        try {
            const schema = JSON.parse(agent.config_schema);
            document.getElementById('customAgentSchema').value = JSON.stringify(schema, null, 2);
        } catch {
            document.getElementById('customAgentSchema').value = agent.config_schema;
        }
    } else {
        document.getElementById('customAgentSchema').value = '';
    }

    new bootstrap.Modal(document.getElementById('customAgentModal')).show();
}

async function saveCustomAgent() {
    const id = document.getElementById('customAgentId').value;

    // Parse comma-separated lists
    const capabilitiesText = document.getElementById('customAgentCapabilities').value;
    const capabilities = capabilitiesText.split(',').map(s => s.trim()).filter(s => s);

    const toolsText = document.getElementById('customAgentTools').value;
    const tools = toolsText.split(',').map(s => s.trim()).filter(s => s);

    // Validate and parse schema
    const schemaText = document.getElementById('customAgentSchema').value.trim();
    let configSchema = null;

    if (schemaText) {
        try {
            configSchema = JSON.parse(schemaText);
        } catch (e) {
            showToast('Invalid JSON in config schema: ' + e.message, 'error');
            return;
        }
    }

    const data = {
        name: document.getElementById('customAgentName').value,
        description: document.getElementById('customAgentDescription').value,
        capabilities: capabilities,
        tools: tools,
        system_prompt: document.getElementById('customAgentPrompt').value,
        config_schema: configSchema
    };

    try {
        const url = id ? `/api/custom-agents/${id}` : '/api/custom-agents';
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save custom agent');
        }

        showToast(id ? 'Custom agent updated successfully' : 'Custom agent created successfully');
        bootstrap.Modal.getInstance(document.getElementById('customAgentModal')).hide();
        loadCustomAgents();
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
}

function confirmDeleteCustomAgent(id) {
    const agent = customAgents.find(a => a.id === id);
    document.getElementById('deleteConfirmText').textContent =
        `Are you sure you want to delete the custom agent "${agent.name}"?`;

    currentDeleteCallback = () => deleteCustomAgent(id);
    document.getElementById('confirmDeleteBtn').onclick = currentDeleteCallback;

    new bootstrap.Modal(document.getElementById('confirmDeleteModal')).show();
}

async function deleteCustomAgent(id) {
    try {
        const response = await fetch(`/api/custom-agents/${id}`, { method: 'DELETE' });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to delete custom agent');
        }

        showToast('Custom agent deleted successfully');
        bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal')).hide();
        loadCustomAgents();
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
}
