-- Migration 004: Add Agents, Teams, and Ratings Tables
-- This migration adds support for agent marketplace with agents, teams, and ratings
-- Note: INTEGER PRIMARY KEY AUTOINCREMENT will be converted to SERIAL PRIMARY KEY for Postgres

-- Create agents table - stores agent definitions for marketplace
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    instructions TEXT NOT NULL,
    tools TEXT NOT NULL,  -- JSON array as TEXT
    skills TEXT,  -- JSON array as TEXT
    default_model TEXT DEFAULT 'sonnet',
    max_turns INTEGER DEFAULT 50,
    allowed_edit_patterns TEXT,  -- JSON array as TEXT
    metadata TEXT,  -- JSON object as TEXT (author, version, etc.)
    source_format TEXT,  -- 'claude', 'roo', 'custom'
    source_file_id INTEGER,  -- Reference to file_uploads(id)
    download_count INTEGER NOT NULL DEFAULT 0,
    rating_average REAL,
    rating_count INTEGER NOT NULL DEFAULT 0,
    is_public BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create teams table - stores agent teams/workflows
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    version TEXT DEFAULT '1.0.0',
    orchestrator TEXT,  -- agent slug for orchestrator
    agents_config TEXT NOT NULL,  -- JSON array: [{slug, role, stage, order}]
    workflow TEXT,  -- JSON object: {type, stages}
    tools TEXT,  -- JSON array as TEXT
    skills TEXT,  -- JSON array as TEXT
    metadata TEXT,  -- JSON object as TEXT
    download_count INTEGER NOT NULL DEFAULT 0,
    rating_average REAL,
    rating_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create ratings table - stores user ratings for agents and teams
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,  -- 'agent' or 'team'
    entity_id INTEGER NOT NULL,
    user_identifier TEXT NOT NULL,  -- Anonymous hash (IP + user agent)
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_type, entity_id, user_identifier)
);

-- Indexes for agents table
CREATE INDEX IF NOT EXISTS idx_agents_slug ON agents(slug);
CREATE INDEX IF NOT EXISTS idx_agents_rating ON agents(rating_average DESC, download_count DESC);
CREATE INDEX IF NOT EXISTS idx_agents_downloads ON agents(download_count DESC);
CREATE INDEX IF NOT EXISTS idx_agents_public ON agents(is_public);
CREATE INDEX IF NOT EXISTS idx_agents_source_file ON agents(source_file_id);

-- Indexes for teams table
CREATE INDEX IF NOT EXISTS idx_teams_slug ON teams(slug);
CREATE INDEX IF NOT EXISTS idx_teams_rating ON teams(rating_average DESC, download_count DESC);
CREATE INDEX IF NOT EXISTS idx_teams_downloads ON teams(download_count DESC);

-- Indexes for ratings table
CREATE INDEX IF NOT EXISTS idx_ratings_entity ON ratings(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_ratings_user ON ratings(user_identifier);

-- ============================================
-- ROLLBACK SQL (for reference only)
-- ============================================
-- DROP INDEX IF EXISTS idx_ratings_user;
-- DROP INDEX IF EXISTS idx_ratings_entity;
-- DROP INDEX IF EXISTS idx_teams_downloads;
-- DROP INDEX IF EXISTS idx_teams_rating;
-- DROP INDEX IF EXISTS idx_teams_slug;
-- DROP INDEX IF EXISTS idx_agents_source_file;
-- DROP INDEX IF EXISTS idx_agents_public;
-- DROP INDEX IF EXISTS idx_agents_downloads;
-- DROP INDEX IF EXISTS idx_agents_rating;
-- DROP INDEX IF EXISTS idx_agents_slug;
-- DROP TABLE IF EXISTS ratings;
-- DROP TABLE IF EXISTS teams;
-- DROP TABLE IF EXISTS agents;
