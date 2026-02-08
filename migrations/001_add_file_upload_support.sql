-- Migration 001: Add File Upload Support
-- This migration adds the file_uploads table and new columns to agent_templates and custom_agents

-- Create file_uploads table
CREATE TABLE IF NOT EXISTS file_uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_format TEXT NOT NULL,  -- 'yaml', 'json', 'md'
    file_size INTEGER NOT NULL,
    upload_status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed'
    parse_result TEXT,  -- JSON string of parsed data
    error_message TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_file_uploads_status ON file_uploads(upload_status);
CREATE INDEX IF NOT EXISTS idx_file_uploads_format ON file_uploads(file_format);

-- Add new columns to agent_templates
-- Note: SQLite doesn't support IF NOT EXISTS for ALTER TABLE ADD COLUMN
-- We'll check if the column exists before adding it
-- For idempotency, we'll use a try-catch approach in the migration function

ALTER TABLE agent_templates ADD COLUMN source_format TEXT;  -- 'claude', 'roo', 'custom', 'manual'
ALTER TABLE agent_templates ADD COLUMN source_file_id INTEGER;  -- Reference to file_uploads
ALTER TABLE agent_templates ADD COLUMN is_imported BOOLEAN NOT NULL DEFAULT 0;

-- Add index for source_file_id
CREATE INDEX IF NOT EXISTS idx_templates_source_file ON agent_templates(source_file_id);

-- Add new columns to custom_agents
ALTER TABLE custom_agents ADD COLUMN source_format TEXT;  -- 'claude', 'roo', 'custom', 'manual'
ALTER TABLE custom_agents ADD COLUMN source_file_id INTEGER;  -- Reference to file_uploads
ALTER TABLE custom_agents ADD COLUMN is_imported BOOLEAN NOT NULL DEFAULT 0;

-- Add index for source_file_id
CREATE INDEX IF NOT EXISTS idx_custom_agents_source_file ON custom_agents(source_file_id);

-- ============================================
-- ROLLBACK SQL (for reference only)
-- ============================================
-- DROP INDEX IF EXISTS idx_custom_agents_source_file;
-- DROP INDEX IF EXISTS idx_templates_source_file;
-- DROP INDEX IF EXISTS idx_file_uploads_format;
-- DROP INDEX IF EXISTS idx_file_uploads_status;
-- DROP TABLE IF EXISTS file_uploads;
-- ALTER TABLE custom_agents DROP COLUMN is_imported;
-- ALTER TABLE custom_agents DROP COLUMN source_file_id;
-- ALTER TABLE custom_agents DROP COLUMN source_format;
-- ALTER TABLE agent_templates DROP COLUMN is_imported;
-- ALTER TABLE agent_templates DROP COLUMN source_file_id;
-- ALTER TABLE agent_templates DROP COLUMN source_format;
