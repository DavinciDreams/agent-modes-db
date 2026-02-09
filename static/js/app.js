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
            if (target === '#templates') loadTemplates();
            else if (target === '#configurations') loadConfigurations();
            else if (target === '#custom-agents') loadCustomAgents();
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
            if (xhr.status === 200) {
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
        const response = await fetch('/api/files');
        const data = await response.json();
        renderRecentUploads(data.uploads || []);
    } catch (error) {
        console.error('Error loading uploads:', error);
    }
}

function renderRecentUploads(uploads) {
    const tbody = document.querySelector('#recentUploadsTable tbody');
    
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
