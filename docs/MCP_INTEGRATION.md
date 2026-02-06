# MCP Integration Guide

**Repository**: [https://github.com/habeneyasu/chimera-factory](https://github.com/habeneyasu/chimera-factory)
**Last Updated**: February 2026

## Overview

This guide covers Model Context Protocol (MCP) integration for Project Chimera, including setup, verification, and troubleshooting.

**Reference**: See `research/tooling_strategy.md` for the strategic separation between Developer Tools (MCP) and Agent Skills (Runtime).

---

## Prerequisites

- Node.js and npm/npx installed
- Cursor IDE (or compatible MCP client)
- Environment variables configured (see Configuration section)

---

## Configuration

### Project-Specific Configuration

**Location**: `.cursor/mcp.json` in project root

This file is configured with the following MCP servers:
- **Filesystem MCP**: File system operations (15 tools)
- **GitHub MCP**: GitHub API operations (26 tools)
- **PostgreSQL MCP**: Database operations (10+ tools)
- **MCP Sense (Tenx)**: Telemetry and flight recorder (required for traceability)

See `docs/mcp.json.example` for configuration template.

### Environment Variables

Create a `.env` file in the project root (not committed to git):

```bash
# GitHub MCP Server
GITHUB_TOKEN=your_github_personal_access_token_here

# PostgreSQL MCP Server
POSTGRES_CONNECTION_STRING=postgresql://user:password@localhost:5432/chimera_dev

# Runtime MCP Servers (for future use)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
IDEOGRAM_API_KEY=your_ideogram_api_key
RUNWAY_API_KEY=your_runway_api_key
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your_weaviate_api_key
```

---

## Verification

### Step 1: Check Cursor IDE Settings

1. Open Cursor IDE
2. Go to **Settings** → **Tools & MCP**
3. Look for **"Installed MCP Servers"** section

### Step 2: Verify Server Status

You should see the following MCP servers:

| Server | Status | Tools Available |
|--------|--------|-----------------|
| **Filesystem MCP** | ✅ Enabled | 15 tools |
| **GitHub MCP** | ✅ Enabled | 26 tools |
| **PostgreSQL MCP** | ✅ Enabled | 10+ tools |
| **MCP Sense (Tenx)** | ✅ Enabled | Telemetry tools |

### Step 3: Test MCP Tools

In Cursor chat, try:
```
@github get repository habeneyasu/chimera-factory
@filesystem read README.md
```

---

## Troubleshooting

### MCP Servers Not Detected

1. Verify `.cursor/mcp.json` exists and is valid JSON
2. Restart Cursor IDE
3. Check Node.js/npx installation: `npx --version`

### GitHub MCP Not Working

1. Create `.env` file with `GITHUB_TOKEN`
2. Generate token: GitHub → Settings → Developer settings → Personal access tokens
3. Restart Cursor IDE

### PostgreSQL MCP Not Working

1. Verify PostgreSQL is running
2. Check `POSTGRES_CONNECTION_STRING` in `.env`
3. Test connection: `psql $POSTGRES_CONNECTION_STRING`

---

## MCP Sense (Tenx) Integration

### Overview

**Status**: ✅ **CONNECTED**

MCP Sense serves as the "Black Box" flight recorder for traceability and governance. It is **required** for project assessment and must be connected at all times.

### Connection Method

MCP Sense is integrated as part of Cursor IDE and operates through Cursor's GitHub authorization. No separate OAuth application is required.

### Connection Status

- **Status**: ✅ **CONNECTED** - MCP Sense interface is accessible
- **GitHub Account**: habeneyasu
- **Repository**: [https://github.com/habeneyasu/chimera-factory](https://github.com/habeneyasu/chimera-factory)
- **Verification**: MCP Sense dashboard visible in Cursor IDE

### Verification Steps

1. Check IDE status bar for MCP Sense indicator
2. Verify connection in MCP Sense dashboard
3. Confirm GitHub account is linked via Cursor integration

### Troubleshooting

If MCP Sense is not connecting:
1. Verify Cursor IDE is authorized on GitHub
2. Check IDE extensions/plugins
3. Restart Cursor IDE
4. Check network connectivity

### Important Notes

- MCP Sense tracks all development work for traceability
- Connection status is verified during project assessment
- All telemetry data is associated with GitHub account: **habeneyasu**

---

## Related Documentation

- **Setup Details**: See `.cursor/mcp.json` for server configuration
- **Tooling Strategy**: See `research/tooling_strategy.md` for MCP vs Skills separation
- **OpenClaw Integration**: See `specs/openclaw_integration.md` for network integration
- **Skill Contracts**: See `skills/README.md` for agent skill definitions

---

**For questions or issues**, refer to the [Model Context Protocol Documentation](https://modelcontextprotocol.io).
