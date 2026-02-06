-- Database Schema: Project Chimera
-- Prepared By: habeneyasu
-- Repository: https://github.com/habeneyasu/chimera-factory
--
-- This schema defines the PostgreSQL database structure for Project Chimera.
-- Video metadata is normalized into a separate table (video_metadata) for
-- efficient querying and storage of video-specific properties.
--
-- See specs/database/erd.md for Entity Relationship Diagram

-- Agents Table
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    persona_id VARCHAR(255) NOT NULL,
    wallet_address VARCHAR(42) NOT NULL UNIQUE, -- Ethereum address format
    status VARCHAR(50) NOT NULL DEFAULT 'sleeping',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Campaigns Table
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Campaign-Agent Association
CREATE TABLE campaign_agents (
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    PRIMARY KEY (campaign_id, agent_id)
);

-- Tasks Table (Task Queue)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type VARCHAR(100) NOT NULL,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    agent_id UUID REFERENCES agents(id),
    campaign_id UUID REFERENCES campaigns(id),
    context JSONB NOT NULL,
    assigned_worker_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Content Plans Table
CREATE TABLE content_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id),
    content_type VARCHAR(50) NOT NULL, -- text, image, video, multimodal
    target_audience TEXT,
    platform VARCHAR(50) NOT NULL, -- twitter, instagram, tiktok, youtube, threads
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    approval_status VARCHAR(50) NOT NULL DEFAULT 'pending', -- auto_approved, pending, rejected
    structure JSONB, -- Content structure (title, sections, etc.)
    key_messages JSONB, -- Array of key messages
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Content Plan - Trend References (Many-to-Many)
CREATE TABLE content_plan_trends (
    plan_id UUID REFERENCES content_plans(id) ON DELETE CASCADE,
    trend_id UUID NOT NULL, -- References trend from external source or internal trend table
    PRIMARY KEY (plan_id, trend_id)
);

-- Content Table
CREATE TABLE content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID REFERENCES content_plans(id),
    agent_id UUID REFERENCES agents(id),
    content_type VARCHAR(50) NOT NULL, -- text, image, video, multimodal
    content_url TEXT NOT NULL,
    metadata JSONB, -- General metadata (platform, format, hashtags, etc.)
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, approved, rejected, published
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Video Metadata Table (Normalized for video content)
CREATE TABLE video_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES content(id) ON DELETE CASCADE UNIQUE,
    duration_seconds FLOAT CHECK (duration_seconds > 0),
    width INTEGER CHECK (width > 0),
    height INTEGER CHECK (height > 0),
    format VARCHAR(50), -- mp4, mov, webm, etc.
    codec VARCHAR(50), -- h264, h265, vp9, etc.
    bitrate_kbps INTEGER,
    frame_rate FLOAT,
    file_size_bytes BIGINT,
    thumbnail_url TEXT,
    has_audio BOOLEAN DEFAULT true,
    has_captions BOOLEAN DEFAULT false,
    caption_url TEXT,
    aspect_ratio VARCHAR(10), -- 16:9, 9:16, 1:1, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Approvals Table (Human-in-the-Loop)
CREATE TABLE approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES content(id),
    plan_id UUID REFERENCES content_plans(id),
    approval_type VARCHAR(50) NOT NULL, -- plan, content
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, approved, rejected, auto_approved
    priority VARCHAR(20) NOT NULL DEFAULT 'medium', -- low, medium, high, urgent
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE, -- Auto-approval deadline
    decided_at TIMESTAMP WITH TIME ZONE,
    decided_by VARCHAR(255), -- User ID who made the decision
    feedback TEXT,
    modifications JSONB -- Requested modifications
);

-- Engagements Table
CREATE TABLE engagements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id),
    platform VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL, -- reply, like, follow, comment
    target_id VARCHAR(255) NOT NULL,
    content_id UUID REFERENCES content(id),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    platform_response JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Transactions Table (On-chain)
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id),
    transaction_hash VARCHAR(66) NOT NULL UNIQUE, -- Ethereum tx hash
    transaction_type VARCHAR(50) NOT NULL, -- transfer, deploy_token, etc.
    amount DECIMAL(18, 8), -- For token transfers
    token_address VARCHAR(42), -- ERC-20 token address
    to_address VARCHAR(42),
    status VARCHAR(50) NOT NULL, -- pending, confirmed, failed
    block_number BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_agent_id ON tasks(agent_id);
CREATE INDEX idx_content_plans_agent_id ON content_plans(agent_id);
CREATE INDEX idx_content_plans_status ON content_plans(approval_status);
CREATE INDEX idx_content_plan_id ON content(plan_id);
CREATE INDEX idx_content_agent_id ON content(agent_id);
CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_content_type ON content(content_type);
CREATE INDEX idx_video_metadata_content_id ON video_metadata(content_id);
CREATE INDEX idx_approvals_content_id ON approvals(content_id);
CREATE INDEX idx_approvals_plan_id ON approvals(plan_id);
CREATE INDEX idx_approvals_status ON approvals(status);
CREATE INDEX idx_engagements_agent_id ON engagements(agent_id);
CREATE INDEX idx_engagements_content_id ON engagements(content_id);
CREATE INDEX idx_transactions_agent_id ON transactions(agent_id);
CREATE INDEX idx_transactions_hash ON transactions(transaction_hash);
