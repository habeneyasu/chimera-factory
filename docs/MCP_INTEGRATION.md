# MCP Integration Guide

**Repository**: [https://github.com/habeneyasu/chimera-factory](https://github.com/habeneyasu/chimera-factory)

## Overview

This guide covers Model Context Protocol (MCP) integration for Project Chimera, including setup, verification, and troubleshooting.

## Prerequisites

- Node.js and npm/npx installed
- Cursor IDE (or compatible MCP client)
- Environment variables configured (see Configuration section)

## Configuration

### Project-Specific Configuration

**Location**: `.cursor/mcp.json` in project root

This file is configured with the following MCP servers:
- **Filesystem MCP**: File system operations
- **GitHub MCP**: GitHub API operations

### Environment Variables

Create a `.env` file in the project root (not committed to git):

```bash
# GitHub MCP Server
GITHUB_TOKEN=your_github_personal_access_token_here

# Runtime MCP Servers (for future use)
POSTGRES_CONNECTION_STRING=postgresql://user:password@localhost:5432/chimera_dev
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
IDEOGRAM_API_KEY=your_ideogram_api_key
RUNWAY_API_KEY=your_runway_api_key
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your_weaviate_api_key
CDP_API_KEY_NAME=your_cdp_key_name
CDP_API_KEY_PRIVATE_KEY=your_cdp_private_key
```

## Verification

### Step 1: Check Cursor IDE Settings

1. Open Cursor IDE
2. Go to **Settings** → **Tools & MCP**
3. Look for **"Installed MCP Servers"** section

### Step 2: Verify Server Status

You should see two MCP servers:

| Server | Status | Tools Available |
|--------|--------|-----------------|
| **GitHub MCP** | ✅ Enabled | 26 tools |
| **Filesystem MCP** | ✅ Enabled | 15 tools |

### Step 3: Test MCP Tools

In Cursor chat, try:
```
@github get repository habeneyasu/chimera-factory
@filesystem read README.md
```

## Troubleshooting

### MCP Servers Not Detected

1. Verify `.cursor/mcp.json` exists and is valid JSON
2. Restart Cursor IDE
3. Check Node.js/npx installation: `npx --version`

### GitHub MCP Not Working

1. Create `.env` file with `GITHUB_TOKEN`
2. Generate token: GitHub → Settings → Developer settings → Personal access tokens
3. Restart Cursor IDE

## MCP Sense (Tenx) Integration

**Status**: ✅ **CONNECTED**

MCP Sense serves as the "Black Box" flight recorder for traceability and governance. Connection verified through Cursor IDE integration.

**Connection Method**: MCP Sense is integrated as part of Cursor IDE and does not require a separate OAuth application. It operates through Cursor's GitHub authorization, which is the expected and correct connection architecture.

**Details**: See `research/mcp_setup_notes.md` for MCP Sense connection status and verification.

## Documentation

- **Setup Details**: See `.cursor/mcp.json` for server configuration
- **Tooling Strategy**: See `research/tooling_strategy.md` for MCP vs Skills separation
- **MCP Sense**: See `research/mcp_setup_notes.md` for Tenx MCP Sense connection
