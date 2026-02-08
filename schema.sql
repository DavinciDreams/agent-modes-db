-- Agent Templates Table
-- Note: Uses INTEGER PRIMARY KEY AUTOINCREMENT for SQLite, will be converted to SERIAL for Postgres
CREATE TABLE IF NOT EXISTS agent_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    is_builtin BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent Configurations Table
CREATE TABLE IF NOT EXISTS agent_configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER,
    name TEXT NOT NULL,
    config_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES agent_templates(id) ON DELETE SET NULL
);

-- Custom Agents Table
CREATE TABLE IF NOT EXISTS custom_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    capabilities TEXT NOT NULL,
    tools TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    config_schema TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_templates_category ON agent_templates(category);
CREATE INDEX IF NOT EXISTS idx_templates_builtin ON agent_templates(is_builtin);
CREATE INDEX IF NOT EXISTS idx_configurations_template ON agent_configurations(template_id);
