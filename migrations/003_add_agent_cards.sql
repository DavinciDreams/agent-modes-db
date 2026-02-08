-- Migration 003: Add Agent Cards Support
-- This migration adds the agent_cards table for storing generated agent cards

-- Create agent_cards table
CREATE TABLE IF NOT EXISTS agent_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,  -- 'template', 'configuration', 'custom_agent'
    entity_id INTEGER NOT NULL,
    card_data TEXT NOT NULL,  -- JSON string of agent card
    card_version TEXT NOT NULL DEFAULT '1.0',
    published BOOLEAN NOT NULL DEFAULT 0,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_type, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_agent_cards_entity ON agent_cards(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_agent_cards_published ON agent_cards(published);

-- ============================================
-- ROLLBACK SQL (for reference only)
-- ============================================
-- DROP INDEX IF EXISTS idx_agent_cards_published;
-- DROP INDEX IF EXISTS idx_agent_cards_entity;
-- DROP TABLE IF EXISTS agent_cards;
