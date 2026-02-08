-- Migration 002: Add Format Conversions Support
-- This migration adds the format_conversions table for tracking conversion history
-- Note: INTEGER PRIMARY KEY AUTOINCREMENT will be converted to SERIAL PRIMARY KEY for Postgres

-- Create format_conversions table
CREATE TABLE IF NOT EXISTS format_conversions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_format TEXT NOT NULL,  -- 'claude', 'roo', 'custom'
    target_format TEXT NOT NULL,  -- 'claude', 'roo', 'custom'
    source_data TEXT NOT NULL,  -- JSON string
    target_data TEXT NOT NULL,  -- JSON string
    conversion_status TEXT NOT NULL DEFAULT 'success',  -- 'success', 'failed'
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conversions_source ON format_conversions(source_format);
CREATE INDEX IF NOT EXISTS idx_conversions_target ON format_conversions(target_format);
CREATE INDEX IF NOT EXISTS idx_conversions_status ON format_conversions(conversion_status);

-- ============================================
-- ROLLBACK SQL (for reference only)
-- ============================================
-- DROP INDEX IF EXISTS idx_conversions_status;
-- DROP INDEX IF EXISTS idx_conversions_target;
-- DROP INDEX IF EXISTS idx_conversions_source;
-- DROP TABLE IF EXISTS format_conversions;