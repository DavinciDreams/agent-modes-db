// Global state
let templates = [];
let configurations = [];
let customAgents = [];
let currentDeleteCallback = null;
let uploadedFiles = [];
let currentAgentCard = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadTemplates();
    loadConfigurations();
    loadCustomAgents();
    initializeDragAndDrop();
    initializeUploadModalDragAndDrop();

    // Set up tab change listeners
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', (e) => {
            const target = e.target.getAttribute('data-bs-target');
            if (target === '#agents') loadAgents();
            else if (target === '#teams') loadTeams();
            else if (target === '#templates') loadTemplates();
            else if (target === '#configurations') loadConfigurations();
            else if (target === '#create-agents') loadCustomAgents();
            else if (target === '#import-convert') {
                loadRecentUploads();
                loadRecentConversions();
            }
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

// ============================================
// Import & Convert Functions
// ============================================

// ============================================
// Drag and Drop Functions
// ============================================

function initializeDragAndDrop() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');

    if (!dropZone || !fileInput) return;

    // Click to browse
    dropZone.addEventListener('click', () => fileInput.click());

    // File input change
    fileInput.addEventListener('change', (e) => handleFileSelect(e.target.files));

    // Drag events
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        handleFileSelect(e.dataTransfer.files);
    });
}

function initializeUploadModalDragAndDrop() {
    const dropZone = document.getElementById('uploadDropZone');
    const fileInput = document.getElementById('uploadFileInput');

    if (!dropZone || !fileInput) return;

    // Click to browse
    dropZone.addEventListener('click', () => fileInput.click());

    // File input change
    fileInput.addEventListener('change', (e) => handleUploadFileSelect(e.target.files));

    // Drag events
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        handleUploadFileSelect(e.dataTransfer.files);
    });
}

function handleFileSelect(files) {
    const filePreviewList = document.getElementById('filePreviewList');
    filePreviewList.innerHTML = '';

    Array.from(files).forEach(file => {
        const format = detectFileFormat(file.name);
        const size = formatFileSize(file.size);
        
        const fileCard = `
            <div class="file-preview-card">
                <div class="d-flex align-items-center">
                    <div class="file-icon ${format}">
                        <i class="fas fa-file-${format === 'json' ? 'code' : format === 'yaml' ? 'code' : 'alt'}"></i>
                    </div>
                    <div class="flex-grow-1 ms-3">
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${size} • ${format.toUpperCase()}</div>
                    </div>
                    <button class="btn btn-sm btn-outline-danger" onclick="removeFile(this)">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
        filePreviewList.insertAdjacentHTML('beforeend', fileCard);
        
        uploadedFiles.push(file);
    });

    if (files.length > 0) {
        showToast(`${files.length} file(s) selected`, 'info');
    }
}

function handleUploadFileSelect(files) {
    const uploadFileList = document.getElementById('uploadFileList');
    uploadFileList.innerHTML = '';

    Array.from(files).forEach(file => {
        const format = detectFileFormat(file.name);
        const size = formatFileSize(file.size);
        
        const fileCard = `
            <div class="file-preview-card">
                <div class="d-flex align-items-center">
                    <div class="file-icon ${format}">
                        <i class="fas fa-file-${format === 'json' ? 'code' : format === 'yaml' ? 'code' : 'alt'}"></i>
                    </div>
                    <div class="flex-grow-1 ms-3">
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${size} • ${format.toUpperCase()}</div>
                    </div>
                    <button class="btn btn-sm btn-outline-danger" onclick="removeUploadFile(this)">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
        uploadFileList.insertAdjacentHTML('beforeend', fileCard);
    });
}

function removeFile(button) {
    const fileCard = button.closest('.file-preview-card');
    const fileName = fileCard.querySelector('.file-name').textContent;
    uploadedFiles = uploadedFiles.filter(f => f.name !== fileName);
    fileCard.remove();
}

function removeUploadFile(button) {
    const fileCard = button.closest('.file-preview-card');
    fileCard.remove();
}

function detectFileFormat(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    if (ext === 'json') return 'json';
    if (ext === 'yaml' || ext === 'yml') return 'yaml';
    if (ext === 'md') return 'md';
    return 'unknown';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// ============================================
// File Upload Functions
// ============================================

function showUploadModal() {
    document.getElementById('uploadFileList').innerHTML = '';
    document.getElementById('uploadProgress').style.display = 'none';
    new bootstrap.Modal(document.getElementById('fileUploadModal')).show();
}

async function uploadFiles() {
    const fileInput = document.getElementById('uploadFileInput');
    const files = fileInput.files;
    
    if (files.length === 0) {
        showToast('Please select files to upload', 'error');
        return;
    }

    const createTemplate = document.getElementById('createTemplate').checked;
    const convertFormat = document.getElementById('convertFormat').checked;

    const formData = new FormData();
    Array.from(files).forEach(file => {
        formData.append('files', file);
    });
    formData.append('create_template', createTemplate);
    formData.append('convert_format', convertFormat);

    // Show progress
    document.getElementById('uploadProgress').style.display = 'block';
    const progressBar = document.getElementById('uploadProgressBar');
    const statusText = document.getElementById('uploadStatus');
    
    try {
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                progressBar.style.width = percentComplete + '%';
                statusText.textContent = `Uploading... ${Math.round(percentComplete)}%`;
            }
        });

        xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                const response = JSON.parse(xhr.responseText);
                showToast('Files uploaded successfully!', 'success');
                bootstrap.Modal.getInstance(document.getElementById('fileUploadModal')).hide();
                loadRecentUploads();
            } else {
                // Log the full error for debugging
                console.error('Upload failed with status:', xhr.status);
                console.error('Response text:', xhr.responseText);

                try {
                    const error = JSON.parse(xhr.responseText);
                    const errorMsg = error.error || error.message || JSON.stringify(error) || 'Unknown error';
                    showToast('Upload failed: ' + errorMsg, 'error');
                } catch (parseError) {
                    console.error('Error parsing error response:', parseError);
                    showToast('Upload failed: ' + (xhr.responseText || 'Unknown error - check console'), 'error');
                }
            }
            document.getElementById('uploadProgress').style.display = 'none';
        });

        xhr.addEventListener('error', () => {
            showToast('Upload failed: Network error', 'error');
            document.getElementById('uploadProgress').style.display = 'none';
        });

        xhr.open('POST', '/api/files/upload/multiple');
        xhr.send(formData);
        
    } catch (error) {
        showToast('Upload failed: ' + error.message, 'error');
        document.getElementById('uploadProgress').style.display = 'none';
    }
}

async function loadRecentUploads() {
    try {
        console.log('Loading recent uploads...');
        const response = await fetch('/api/files');

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Received uploads data:', data);
        console.log('Number of uploads:', data.uploads?.length || 0);

        renderRecentUploads(data.uploads || []);
    } catch (error) {
        console.error('Error loading uploads:', error);
        showToast('Failed to load recent uploads: ' + error.message, 'danger');
    }
}

function renderRecentUploads(uploads) {
    const tbody = document.querySelector('#recentUploadsTable tbody');

    // Add null check
    if (!tbody) {
        console.error('Recent uploads table not found in DOM');
        showToast('Error: Upload table not found', 'danger');
        return;
    }

    if (uploads.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-muted text-center">No recent uploads</td></tr>';
        return;
    }

    tbody.innerHTML = uploads.map(upload => `
        <tr>
            <td class="text-break">${upload.original_filename}</td>
            <td><span class="format-badge ${upload.file_format}">${upload.file_format.toUpperCase()}</span></td>
            <td>${formatFileSize(upload.file_size)}</td>
            <td><span class="status-badge ${upload.upload_status}">${upload.upload_status}</span></td>
            <td>${formatDate(upload.uploaded_at)}</td>
            <td>
                <button class="btn btn-sm btn-outline-info" onclick="viewUploadDetails(${upload.id})">
                    <i class="fas fa-eye"></i>
                </button>
                ${upload.upload_status === 'completed' ? `
                    <button class="btn btn-sm btn-outline-success" onclick="downloadUpload(${upload.id})">
                        <i class="fas fa-download"></i>
                    </button>
                ` : ''}
            </td>
        </tr>
    `).join('');
}

async function viewUploadDetails(id) {
    try {
        const response = await fetch(`/api/files/${id}`);
        const upload = await response.json();
        
        // Show details in a modal or alert
        alert(`Upload Details:\n\nFilename: ${upload.original_filename}\nFormat: ${upload.file_format}\nSize: ${formatFileSize(upload.file_size)}\nStatus: ${upload.upload_status}\nUploaded: ${formatDate(upload.uploaded_at)}`);
    } catch (error) {
        showToast('Error loading upload details: ' + error.message, 'error');
    }
}

async function downloadUpload(id) {
    try {
        const response = await fetch(`/api/files/${id}`);
        const upload = await response.json();
        
        if (upload.parse_result) {
            const data = typeof upload.parse_result === 'string' ? JSON.parse(upload.parse_result) : upload.parse_result;
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = upload.original_filename || `upload_${id}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            showToast('File downloaded successfully', 'success');
        } else {
            showToast('No data available for download', 'error');
        }
    } catch (error) {
        showToast('Error downloading file: ' + error.message, 'error');
    }
}

// ============================================
// Format Converter Functions
// ============================================

function showFormatConverter() {
    document.getElementById('formatConverterCard').style.display = 'block';
    document.getElementById('agentCardsCard').style.display = 'none';
    document.getElementById('formatConverterCard').scrollIntoView({ behavior: 'smooth' });
}

function clearConverter() {
    document.getElementById('converterInput').value = '';
    document.getElementById('converterResult').value = '';
    document.getElementById('converterOutput').style.display = 'none';
}

async function convertFormat() {
    const sourceFormat = document.getElementById('sourceFormat').value;
    const targetFormat = document.getElementById('targetFormat').value;
    const content = document.getElementById('converterInput').value;

    if (!content.trim()) {
        showToast('Please enter content to convert', 'error');
        return;
    }

    if (sourceFormat === targetFormat) {
        showToast('Source and target formats are the same', 'error');
        return;
    }

    try {
        const response = await fetch('/api/convert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source_format: sourceFormat,
                target_format: targetFormat,
                content: content
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Conversion failed');
        }

        const result = await response.json();
        document.getElementById('converterResult').value = JSON.stringify(result.converted_data, null, 2);
        document.getElementById('converterOutput').style.display = 'block';
        showToast('Format converted successfully!', 'success');
        
        // Load recent conversions
        loadRecentConversions();
    } catch (error) {
        showToast('Conversion failed: ' + error.message, 'error');
    }
}

function copyConvertedOutput() {
    const output = document.getElementById('converterResult');
    output.select();
    document.execCommand('copy');
    showToast('Copied to clipboard!', 'success');
}

function downloadConvertedOutput() {
    const content = document.getElementById('converterResult').value;
    const targetFormat = document.getElementById('targetFormat').value;
    const blob = new Blob([content], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `converted_${targetFormat}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    showToast('File downloaded successfully', 'success');
}

async function loadRecentConversions() {
    try {
        const response = await fetch('/api/convert/history');
        const data = await response.json();
        renderRecentConversions(data.conversions || []);
    } catch (error) {
        console.error('Error loading conversions:', error);
    }
}

function renderRecentConversions(conversions) {
    const tbody = document.querySelector('#recentConversionsTable tbody');
    
    if (conversions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-muted text-center">No recent conversions</td></tr>';
        return;
    }

    tbody.innerHTML = conversions.map(conv => `
        <tr>
            <td><span class="format-badge ${conv.source_format}">${conv.source_format.toUpperCase()}</span></td>
            <td><span class="format-badge ${conv.target_format}">${conv.target_format.toUpperCase()}</span></td>
            <td><span class="status-badge ${conv.conversion_status}">${conv.conversion_status}</span></td>
            <td>${formatDate(conv.created_at)}</td>
            <td>
                <button class="btn btn-sm btn-outline-info" onclick="viewConversionDetails(${conv.id})">
                    <i class="fas fa-eye"></i>
                </button>
                ${conv.conversion_status === 'success' ? `
                    <button class="btn btn-sm btn-outline-success" onclick="downloadConversion(${conv.id})">
                        <i class="fas fa-download"></i>
                    </button>
                ` : ''}
            </td>
        </tr>
    `).join('');
}

async function viewConversionDetails(id) {
    try {
        const response = await fetch('/api/convert/history');
        const data = await response.json();
        const conversion = data.conversions.find(c => c.id === id);
        
        if (conversion) {
            alert(`Conversion Details:\n\nSource: ${conversion.source_format}\nTarget: ${conversion.target_format}\nStatus: ${conversion.conversion_status}\nCreated: ${formatDate(conversion.created_at)}`);
        } else {
            showToast('Conversion not found', 'error');
        }
    } catch (error) {
        showToast('Error loading conversion details: ' + error.message, 'error');
    }
}

async function downloadConversion(id) {
    try {
        const response = await fetch('/api/convert/history');
        const data = await response.json();
        const conversion = data.conversions.find(c => c.id === id);
        
        if (conversion && conversion.target_data) {
            const targetData = typeof conversion.target_data === 'string' ? JSON.parse(conversion.target_data) : conversion.target_data;
            const blob = new Blob([JSON.stringify(targetData, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `conversion_${id}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            showToast('File downloaded successfully', 'success');
        } else {
            showToast('No data available for download', 'error');
        }
    } catch (error) {
        showToast('Error downloading file: ' + error.message, 'error');
    }
}

// ============================================
// Agent Cards Functions
// ============================================

function showAgentCards() {
    document.getElementById('agentCardsCard').style.display = 'block';
    document.getElementById('formatConverterCard').style.display = 'none';
    loadAgentCards();
    document.getElementById('agentCardsCard').scrollIntoView({ behavior: 'smooth' });
}

async function loadAgentCards() {
    const entityType = document.getElementById('cardEntityType').value;
    const grid = document.getElementById('agentCardsGrid');
    
    grid.innerHTML = '<div class="col-12 text-center"><div class="spinner-border" role="status"></div></div>';
    
    try {
        const response = await fetch(`/api/agent-cards?entity_type=${entityType}`);
        const data = await response.json();
        renderAgentCards(data.cards || []);
    } catch (error) {
        grid.innerHTML = '<div class="col-12"><p class="text-muted text-center">Error loading agent cards</p></div>';
        console.error('Error loading agent cards:', error);
    }
}

function renderAgentCards(cards) {
    const grid = document.getElementById('agentCardsGrid');
    
    if (cards.length === 0) {
        grid.innerHTML = '<div class="col-12"><p class="text-muted text-center">No agent cards found</p></div>';
        return;
    }

    grid.innerHTML = cards.map(card => {
        const cardData = JSON.parse(card.card_data);
        const isValid = cardData && cardData.name && cardData.description;
        
        return `
            <div class="col-md-6 col-lg-4">
                <div class="agent-card-preview h-100">
                    <div class="card-header">
                        <h6 class="card-title mb-0">${cardData.name || 'Unknown'}</h6>
                        <p class="card-description mb-0">${cardData.description || 'No description'}</p>
                    </div>
                    <div class="card-meta">
                        <span class="badge bg-secondary">${card.entity_type}</span>
                        <span class="badge bg-info">v${card.card_version}</span>
                        ${card.published ? '<span class="badge bg-success">Published</span>' : '<span class="badge bg-warning">Draft</span>'}
                    </div>
                    <div class="validation-status ${isValid ? 'valid' : 'invalid'}">
                        <i class="fas fa-${isValid ? 'check-circle' : 'exclamation-circle'}"></i>
                        <span>${isValid ? 'Valid' : 'Invalid'}</span>
                    </div>
                    <div class="card-actions">
                        <button class="btn btn-sm btn-outline-primary" onclick="viewAgentCard(${card.id})">
                            <i class="fas fa-eye"></i> View
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="copyAgentCardData(${card.id})">
                            <i class="fas fa-copy"></i> Copy
                        </button>
                        ${!card.published ? `
                            <button class="btn btn-sm btn-outline-info" onclick="publishAgentCard(${card.id})">
                                <i class="fas fa-upload"></i> Publish
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

async function viewAgentCard(id) {
    try {
        const response = await fetch(`/api/agent-cards/${id}`);
        const card = await response.json();
        const cardData = JSON.parse(card.card_data);
        
        currentAgentCard = card;
        
        // Populate details
        const detailsHtml = `
            <div class="detail-row">
                <span class="detail-label">Name:</span>
                <span class="detail-value">${cardData.name || 'N/A'}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Description:</span>
                <span class="detail-value">${cardData.description || 'N/A'}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Entity Type:</span>
                <span class="detail-value">${card.entity_type}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Entity ID:</span>
                <span class="detail-value">${card.entity_id}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Version:</span>
                <span class="detail-value">${card.card_version}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Published:</span>
                <span class="detail-value">${card.published ? 'Yes' : 'No'}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Generated:</span>
                <span class="detail-value">${formatDate(card.generated_at)}</span>
            </div>
        `;
        
        document.getElementById('agentCardDetails').innerHTML = detailsHtml;
        document.getElementById('agentCardJson').value = JSON.stringify(cardData, null, 2);
        
        new bootstrap.Modal(document.getElementById('agentCardModal')).show();
    } catch (error) {
        showToast('Error loading agent card: ' + error.message, 'error');
    }
}

function copyAgentCard() {
    const jsonContent = document.getElementById('agentCardJson');
    jsonContent.select();
    document.execCommand('copy');
    showToast('Copied to clipboard!', 'success');
}

async function copyAgentCardData(id) {
    try {
        const response = await fetch(`/api/agent-cards/${id}`);
        const card = await response.json();
        const cardData = JSON.parse(card.card_data);
        
        navigator.clipboard.writeText(JSON.stringify(cardData, null, 2));
        showToast('Agent card copied to clipboard!', 'success');
    } catch (error) {
        showToast('Error copying agent card: ' + error.message, 'error');
    }
}

function downloadAgentCardJSON() {
    if (!currentAgentCard) return;
    
    const cardData = JSON.parse(currentAgentCard.card_data);
    const blob = new Blob([JSON.stringify(cardData, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agent_card_${currentAgentCard.id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    showToast('JSON file downloaded successfully', 'success');
}

function downloadAgentCardYAML() {
    if (!currentAgentCard) return;
    
    const cardData = JSON.parse(currentAgentCard.card_data);
    // Simple YAML conversion (for production, use a proper YAML library)
    let yamlContent = `name: ${cardData.name}\n`;
    yamlContent += `description: ${cardData.description}\n`;
    if (cardData.capabilities) {
        yamlContent += `capabilities:\n`;
        cardData.capabilities.forEach(cap => {
            yamlContent += `  - ${cap}\n`;
        });
    }
    
    const blob = new Blob([yamlContent], { type: 'text/yaml' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agent_card_${currentAgentCard.id}.yaml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    showToast('YAML file downloaded successfully', 'success');
}

async function publishAgentCard(id) {
    try {
        const response = await fetch(`/api/agent-cards/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ published: true })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to publish agent card');
        }
        
        showToast('Agent card published successfully!', 'success');
        loadAgentCards();
    } catch (error) {
        showToast('Error publishing agent card: ' + error.message, 'error');
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

// ============================================
// Agents Page
// ============================================

let currentAgentSort = 'rating';
let currentAgentOrder = 'desc';

async function loadAgents() {
    try {
        const response = await fetch(`/api/agents?sort=${currentAgentSort}&order=${currentAgentOrder}`);
        const data = await response.json();
        renderAgents(data.agents || []);
    } catch (error) {
        console.error('Error loading agents:', error);
        showToast('Failed to load agents', 'error');
    }
}

function renderAgents(agents) {
    const container = document.getElementById('agentsContainer');

    if (agents.length === 0) {
        container.innerHTML = '<div class="col-12 text-center text-muted">No agents found</div>';
        return;
    }

    container.innerHTML = agents.map(agent => `
        <div class="col-md-4 mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <h5 class="card-title">🤖 ${agent.name}</h5>
                    <p class="card-text text-muted">${agent.description || 'No description'}</p>

                    <div class="mb-2">
                        <span class="badge bg-primary">${agent.tools?.length || 0} tools</span>
                        <span class="badge bg-info">${agent.default_model}</span>
                    </div>

                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <div>
                            ${renderStars(agent.rating_average || 0)}
                            <small class="text-muted">(${agent.rating_count || 0})</small>
                        </div>
                        <div>
                            <small><i class="fas fa-download"></i> ${agent.download_count || 0}</small>
                        </div>
                    </div>
                </div>
                <div class="card-footer bg-transparent">
                    <button class="btn btn-sm btn-outline-primary" onclick="viewAgent(${agent.id})">
                        <i class="fas fa-eye"></i> Details
                    </button>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-success dropdown-toggle" data-bs-toggle="dropdown">
                            <i class="fas fa-download"></i> Download
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#" onclick="downloadAgent(${agent.id}, 'claude')">Claude Format</a></li>
                            <li><a class="dropdown-item" href="#" onclick="downloadAgent(${agent.id}, 'roo')">Roo Format</a></li>
                            <li><a class="dropdown-item" href="#" onclick="downloadAgent(${agent.id}, 'universal')">Universal</a></li>
                        </ul>
                    </div>
                    <button class="btn btn-sm btn-warning" onclick="showRatingModal('agent', ${agent.id}, '${agent.name}')">
                        <i class="fas fa-star"></i> Rate
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function renderStars(rating) {
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 >= 0.5;
    let stars = '';

    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star text-warning"></i>';
    }
    if (halfStar) {
        stars += '<i class="fas fa-star-half-alt text-warning"></i>';
    }
    for (let i = fullStars + (halfStar ? 1 : 0); i < 5; i++) {
        stars += '<i class="far fa-star text-warning"></i>';
    }

    return stars;
}

function sortAgents(sortBy) {
    currentAgentSort = sortBy;
    loadAgents();
}

async function searchAgents() {
    const query = document.getElementById('agentSearch').value;
    try {
        const response = await fetch(`/api/agents?search=${encodeURIComponent(query)}&sort=${currentAgentSort}`);
        const data = await response.json();
        renderAgents(data.agents || []);
    } catch (error) {
        console.error('Error searching agents:', error);
        showToast('Search failed', 'error');
    }
}

async function viewAgent(agentId) {
    try {
        const response = await fetch(`/api/agents/${agentId}`);
        const agent = await response.json();

        document.getElementById('agentDetailTitle').textContent = agent.name;
        document.getElementById('agentDetailBody').innerHTML = `
            <p><strong>Slug:</strong> ${agent.slug}</p>
            <p><strong>Description:</strong> ${agent.description || 'No description'}</p>
            <p><strong>Model:</strong> ${agent.default_model}</p>
            <p><strong>Max Turns:</strong> ${agent.max_turns}</p>

            <h6>Tools:</h6>
            <p>${(agent.tools || []).map(t => `<span class="badge bg-primary">${t}</span>`).join(' ')}</p>

            ${agent.skills?.length ? `<h6>Skills:</h6><p>${agent.skills.map(s => `<span class="badge bg-info">${s}</span>`).join(' ')}</p>` : ''}

            <h6>Instructions:</h6>
            <pre class="bg-light p-2" style="max-height: 300px; overflow-y: auto;">${agent.instructions}</pre>

            <h6>Ratings:</h6>
            <div>${renderStars(agent.rating_average || 0)} (${agent.rating_count || 0} ratings)</div>

            ${(agent.ratings || []).length > 0 ? `
                <div class="mt-3">
                    <h6>Reviews:</h6>
                    ${agent.ratings.slice(0, 5).map(r => `
                        <div class="border-bottom pb-2 mb-2">
                            <div>${renderStars(r.rating)}</div>
                            ${r.review ? `<p class="mb-0 small">${r.review}</p>` : ''}
                            <small class="text-muted">${new Date(r.created_at).toLocaleDateString()}</small>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        `;

        new bootstrap.Modal(document.getElementById('agentDetailModal')).show();
    } catch (error) {
        console.error('Error loading agent:', error);
        showToast('Failed to load agent details', 'error');
    }
}

async function downloadAgent(agentId, format) {
    try {
        const response = await fetch(`/api/agents/${agentId}/download?format=${format}`);
        const agent = await response.json();

        const blob = new Blob([JSON.stringify(agent, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${agent.slug || 'agent'}.${format}.json`;
        a.click();
        URL.revokeObjectURL(url);

        showToast(`Downloaded ${agent.name} in ${format} format`, 'success');
    } catch (error) {
        console.error('Error downloading agent:', error);
        showToast('Download failed', 'error');
    }
}

// ============================================
// Teams Page
// ============================================

let currentTeamSort = 'rating';

async function loadTeams() {
    try {
        const response = await fetch(`/api/teams?sort=${currentTeamSort}`);
        const data = await response.json();
        renderTeams(data.teams || []);
    } catch (error) {
        console.error('Error loading teams:', error);
        showToast('Failed to load teams', 'error');
    }
}

function renderTeams(teams) {
    const container = document.getElementById('teamsContainer');

    if (teams.length === 0) {
        container.innerHTML = '<div class="col-12 text-center text-muted">No teams found</div>';
        return;
    }

    container.innerHTML = teams.map(team => `
        <div class="col-md-6 mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <h5 class="card-title">👥 ${team.name}</h5>
                    <p class="card-text text-muted">${team.description || 'No description'}</p>

                    <div class="mb-2">
                        <span class="badge bg-success">${team.agents?.length || 0} agents</span>
                        ${team.orchestrator ? `<span class="badge bg-info">Orchestrated</span>` : ''}
                    </div>

                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <div>
                            ${renderStars(team.rating_average || 0)}
                            <small class="text-muted">(${team.rating_count || 0})</small>
                        </div>
                        <div>
                            <small><i class="fas fa-download"></i> ${team.download_count || 0}</small>
                        </div>
                    </div>
                </div>
                <div class="card-footer bg-transparent">
                    <button class="btn btn-sm btn-outline-primary" onclick="viewTeam(${team.id})">
                        <i class="fas fa-eye"></i> Details
                    </button>
                    <button class="btn btn-sm btn-success" onclick="downloadTeam(${team.id})">
                        <i class="fas fa-download"></i> Download
                    </button>
                    <button class="btn btn-sm btn-warning" onclick="showRatingModal('team', ${team.id}, '${team.name}')">
                        <i class="fas fa-star"></i> Rate
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function sortTeams(sortBy) {
    currentTeamSort = sortBy;
    loadTeams();
}

async function viewTeam(teamId) {
    try {
        const response = await fetch(`/api/teams/${teamId}`);
        const team = await response.json();

        document.getElementById('teamDetailTitle').textContent = team.name;
        document.getElementById('teamDetailBody').innerHTML = `
            <p><strong>Slug:</strong> ${team.slug}</p>
            <p><strong>Description:</strong> ${team.description || 'No description'}</p>
            <p><strong>Version:</strong> ${team.version || '1.0.0'}</p>
            ${team.orchestrator ? `<p><strong>Orchestrator:</strong> ${team.orchestrator}</p>` : ''}

            <h6>Agents (${team.agents?.length || 0}):</h6>
            <ul>
                ${(team.agents || []).map(a => `<li>${a.slug}${a.role ? ` - ${a.role}` : ''}</li>`).join('')}
            </ul>

            ${team.workflow ? `
                <h6>Workflow:</h6>
                <p><strong>Type:</strong> ${team.workflow.type}</p>
                ${team.workflow.stages ? `<p><strong>Stages:</strong> ${team.workflow.stages.join(' → ')}</p>` : ''}
            ` : ''}

            <h6>Ratings:</h6>
            <div>${renderStars(team.rating_average || 0)} (${team.rating_count || 0} ratings)</div>
        `;

        new bootstrap.Modal(document.getElementById('teamDetailModal')).show();
    } catch (error) {
        console.error('Error loading team:', error);
        showToast('Failed to load team details', 'error');
    }
}

async function downloadTeam(teamId) {
    try {
        const response = await fetch(`/api/teams/${teamId}/download`);
        const team = await response.json();

        const blob = new Blob([JSON.stringify(team, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${team.slug || 'team'}.json`;
        a.click();
        URL.revokeObjectURL(url);

        showToast(`Downloaded ${team.name}`, 'success');
    } catch (error) {
        console.error('Error downloading team:', error);
        showToast('Download failed', 'error');
    }
}

// ============================================
// Create Team Modal
// ============================================

let selectedTeamAgents = [];

function showCreateTeamModal() {
    selectedTeamAgents = [];
    document.getElementById('createTeamForm').reset();
    document.getElementById('selectedAgentsList').innerHTML = '';
    new bootstrap.Modal(document.getElementById('createTeamModal')).show();
}

async function searchAgentsForTeam() {
    const query = document.getElementById('teamAgentSearch').value;
    try {
        const response = await fetch(`/api/agents?search=${encodeURIComponent(query)}&limit=10`);
        const data = await response.json();

        const results = document.getElementById('teamAgentResults');
        results.innerHTML = data.agents.map(agent => `
            <div class="border p-2 mb-1 d-flex justify-content-between align-items-center">
                <div>
                    <strong>${agent.name}</strong>
                    <small class="text-muted d-block">${agent.description || ''}</small>
                </div>
                <button class="btn btn-sm btn-primary" onclick="addAgentToTeam('${agent.slug}', '${agent.name}')">
                    <i class="fas fa-plus"></i> Add
                </button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error searching agents:', error);
    }
}

function addAgentToTeam(slug, name) {
    if (selectedTeamAgents.find(a => a.slug === slug)) {
        showToast('Agent already added', 'info');
        return;
    }

    selectedTeamAgents.push({ slug, name, role: '' });
    updateSelectedAgentsList();
}

function removeAgentFromTeam(slug) {
    selectedTeamAgents = selectedTeamAgents.filter(a => a.slug !== slug);
    updateSelectedAgentsList();
}

function updateSelectedAgentsList() {
    const list = document.getElementById('selectedAgentsList');

    if (selectedTeamAgents.length === 0) {
        list.innerHTML = '<p class="text-muted mb-0">No agents selected</p>';
        return;
    }

    list.innerHTML = selectedTeamAgents.map((agent, i) => `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <div class="flex-grow-1">
                <strong>${agent.name}</strong>
                <input type="text" class="form-control form-control-sm mt-1" placeholder="Role (e.g., Frontend Developer)"
                       onchange="selectedTeamAgents[${i}].role = this.value">
            </div>
            <button class="btn btn-sm btn-danger ms-2" onclick="removeAgentFromTeam('${agent.slug}')">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `).join('');
}

async function saveTeam() {
    const slug = document.getElementById('teamSlug').value;
    const name = document.getElementById('teamName').value;
    const description = document.getElementById('teamDescription').value;

    if (!slug || !name || selectedTeamAgents.length === 0) {
        showToast('Please fill required fields and add at least one agent', 'error');
        return;
    }

    try {
        const response = await fetch('/api/teams', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                slug,
                name,
                description,
                agents: selectedTeamAgents
            })
        });

        if (response.ok) {
            showToast('Team created successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('createTeamModal')).hide();
            loadTeams();
        } else {
            const error = await response.json();
            showToast('Failed to create team: ' + (error.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error creating team:', error);
        showToast('Failed to create team', 'error');
    }
}

// ============================================
// Rating System
// ============================================

let currentRatingEntity = { type: '', id: 0, name: '' };
let selectedRating = 0;

function showRatingModal(entityType, entityId, entityName) {
    currentRatingEntity = { type: entityType, id: entityId, name: entityName };
    selectedRating = 0;

    document.getElementById('ratingEntityName').textContent = entityName;
    document.getElementById('ratingReview').value = '';

    // Reset stars
    document.querySelectorAll('#starRating i').forEach(star => {
        star.className = 'far fa-star';
    });

    // Add click handlers
    document.querySelectorAll('#starRating i').forEach((star, index) => {
        star.onclick = () => selectStar(index + 1);
        star.onmouseover = () => hoverStars(index + 1);
    });

    document.getElementById('starRating').onmouseleave = () => hoverStars(selectedRating);

    new bootstrap.Modal(document.getElementById('ratingModal')).show();
}

function selectStar(rating) {
    selectedRating = rating;
    hoverStars(rating);
}

function hoverStars(rating) {
    document.querySelectorAll('#starRating i').forEach((star, index) => {
        star.className = index < rating ? 'fas fa-star text-warning' : 'far fa-star';
    });
}

async function submitRating() {
    if (selectedRating === 0) {
        showToast('Please select a rating', 'info');
        return;
    }

    const review = document.getElementById('ratingReview').value;

    try {
        const url = `/api/${currentRatingEntity.type}s/${currentRatingEntity.id}/rate`;
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rating: selectedRating, review })
        });

        if (response.ok) {
            showToast('Rating submitted successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('ratingModal')).hide();

            // Reload the appropriate list
            if (currentRatingEntity.type === 'agent') {
                loadAgents();
            } else {
                loadTeams();
            }
        } else {
            const error = await response.json();
            showToast('Failed to submit rating: ' + (error.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error submitting rating:', error);
        showToast('Failed to submit rating', 'error');
    }
}
