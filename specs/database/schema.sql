-- Database Schema: Project Chimera
-- Prepared By: habeneyasu
-- Repository: https://github.com/habeneyasu/chimera-factory

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

-- Content Table
CREATE TABLE content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id),
    content_type VARCHAR(50) NOT NULL, -- text, image, video
    content_url TEXT NOT NULL,
    metadata JSONB,
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, approved, rejected, published
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
CREATE INDEX idx_content_agent_id ON content(agent_id);
CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_engagements_agent_id ON engagements(agent_id);
CREATE INDEX idx_transactions_agent_id ON transactions(agent_id);
CREATE INDEX idx_transactions_hash ON transactions(transaction_hash);
