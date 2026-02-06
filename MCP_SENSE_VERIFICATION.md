# MCP Sense (Tenx) Verification Guide

**Purpose**: Verify that Tenx MCP Sense is active and tracking your "Thinking" for project assessment.

---

## ✅ Critical Requirements

1. **MCP Sense must be active** during all development work
2. **GitHub account must match** the account used for project submission
3. **Connection must be verified** before submission

---

## 🔍 Step 1: Verify MCP Configuration

### Check `.cursor/mcp.json`

The MCP Sense server should be configured in `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "tenxfeedbackanalytics": {
      "name": "tenxanalysismcp",
      "url": "https://mcppulse.10academy.org/proxy",
      "headers": {
        "X-Device": "linux",
        "X-Coding-Tool": "cursor"
      },
      "description": "MCP Sense telemetry and flight recorder for traceability and governance"
    }
  }
}
```

**Action**: Verify this configuration exists in your `.cursor/mcp.json` file.

---

## 🔍 Step 2: Verify Cursor IDE Connection

### Check Cursor IDE Settings

1. **Open Cursor IDE**
2. **Go to Settings** → **Tools & MCP** (or **Features** → **MCP**)
3. **Look for "Installed MCP Servers"** section
4. **Verify "tenxfeedbackanalytics" or "MCP Sense"** is listed and shows ✅ **Enabled**

### Check Status Bar

- Look for MCP Sense indicator in Cursor IDE status bar
- Should show connection status (connected/disconnected)

---

## 🔍 Step 3: Verify GitHub Account Connection

### Critical: GitHub Account Must Match Submission Account

**Your GitHub Account**: `habeneyasu` (must match submission)

### Verify GitHub Authorization

1. **Check Cursor IDE GitHub Integration**:
   - Go to **Settings** → **GitHub** (or **Account**)
   - Verify your GitHub account is connected
   - Should show: `habeneyasu` or your GitHub username

2. **Verify on GitHub**:
   - Go to GitHub.com → **Settings** → **Applications** → **Authorized OAuth Apps**
   - Look for **Cursor** or **MCP Sense** in the list
   - Verify it's authorized with the correct account

3. **Verify Repository Connection**:
   - Repository: `https://github.com/habeneyasu/chimera-factory`
   - Ensure you're working in the correct repository
   - Verify commits are made with the correct GitHub account

---

## 🔍 Step 4: Test MCP Sense Connection

### Method 1: Check MCP Tools Available

In Cursor chat, you should be able to see MCP Sense tools. Try asking:

```
"What MCP tools are available?"
```

Or check if you can see tools like:
- `mcp_tenxfeedbackanalytics_log_passage_time_trigger`
- `mcp_tenxfeedbackanalytics_log_performance_outlier_trigger`
- `mcp_tenxfeedbackanalytics_list_managed_servers`

### Method 2: Check MCP Resources

MCP Sense should be listed as an available MCP server. You can verify this programmatically or through Cursor's MCP interface.

### Method 3: Verify Active Connection

Look for indicators that MCP Sense is actively tracking:
- Check Cursor IDE logs/console for MCP Sense activity
- Verify no connection errors in IDE
- Check network activity (if possible) to `mcppulse.10academy.org`

---

## 🔍 Step 5: Verify "Thinking" is Being Tracked

### What is "Thinking"?

MCP Sense tracks your development "Thinking" through:
- **Passage of Time Triggers**: Periodic snapshots of your work
- **Performance Outlier Triggers**: Exceptional good/poor performance patterns
- **Interaction Patterns**: How you work with the AI agent

### How to Verify Tracking

1. **Work on the project** for at least 10-15 minutes
2. **Interact with the AI agent** (ask questions, make requests)
3. **Make code changes** (edit files, run tests)
4. **Check for MCP Sense activity** in IDE logs or status

### Expected Behavior

- MCP Sense should be silently tracking in the background
- No visible UI is required (it works through the MCP protocol)
- Tracking happens automatically when MCP Sense is connected

---

## ✅ Pre-Submission Checklist

Before submitting your project, verify:

- [ ] `.cursor/mcp.json` contains `tenxfeedbackanalytics` configuration
- [ ] Cursor IDE shows MCP Sense as **Enabled** in settings
- [ ] GitHub account connected to Cursor matches submission account (`habeneyasu`)
- [ ] GitHub OAuth authorization is active (check GitHub Settings → Applications)
- [ ] Repository is correct: `habeneyasu/chimera-factory`
- [ ] MCP Sense tools are available (check via chat or MCP interface)
- [ ] No connection errors in Cursor IDE
- [ ] You've been working with the project while MCP Sense is active

---

## 🚨 Troubleshooting

### MCP Sense Not Showing in Cursor IDE

1. **Restart Cursor IDE**
2. **Check `.cursor/mcp.json`** is valid JSON
3. **Verify network connectivity** to `mcppulse.10academy.org`
4. **Check Cursor IDE version** (ensure it supports MCP)

### GitHub Account Mismatch

1. **Disconnect GitHub** from Cursor IDE
2. **Reconnect with correct account** (`habeneyasu`)
3. **Verify in GitHub Settings** → Applications → Authorized OAuth Apps
4. **Restart Cursor IDE**

### Connection Errors

1. **Check internet connection**
2. **Verify proxy/firewall** isn't blocking `mcppulse.10academy.org`
3. **Check Cursor IDE logs** for error messages
4. **Try restarting Cursor IDE**

### Can't Verify Tracking

- MCP Sense works silently in the background
- No visible UI is required
- As long as it's configured and enabled, it should be tracking
- The assessment team will verify telemetry on their end

---

## 📝 Verification Commands

### Check MCP Configuration

```bash
# Verify .cursor/mcp.json exists and contains tenxfeedbackanalytics
cat .cursor/mcp.json | grep -i "tenx\|sense"

# Check if file is valid JSON
cat .cursor/mcp.json | python3 -m json.tool > /dev/null && echo "✅ Valid JSON" || echo "❌ Invalid JSON"
```

### Check GitHub Account

```bash
# Verify git is configured with correct account
git config user.name
git config user.email

# Check recent commits
git log --format='%an <%ae>' -5
```

---

## 🎯 Final Verification Steps

Before submission, run these checks:

1. **Configuration Check**:
   ```bash
   [ -f .cursor/mcp.json ] && echo "✅ MCP config exists" || echo "❌ MCP config missing"
   grep -q "tenxfeedbackanalytics" .cursor/mcp.json && echo "✅ MCP Sense configured" || echo "❌ MCP Sense not configured"
   ```

2. **GitHub Account Check**:
   ```bash
   git config user.name
   # Should match your submission GitHub account
   ```

3. **Repository Check**:
   ```bash
   git remote -v
   # Should show: habeneyasu/chimera-factory
   ```

---

## 📌 Important Notes

1. **MCP Sense must be active** during development work, not just at submission time
2. **GitHub account must match** - if you've been working with a different account, reconnect
3. **No separate login required** - MCP Sense uses Cursor IDE's GitHub authorization
4. **Tracking is automatic** - no manual action needed once configured
5. **Assessment team will verify** - they'll check telemetry data on their end

---

## ✅ Submission Confirmation

**Before submitting, confirm**:

- ✅ MCP Sense is configured in `.cursor/mcp.json`
- ✅ Cursor IDE shows MCP Sense as enabled
- ✅ GitHub account matches submission account (`habeneyasu`)
- ✅ Repository is correct (`habeneyasu/chimera-factory`)
- ✅ You've been actively working on the project with MCP Sense enabled

**If all checks pass, you're ready to submit!** 🎉

---

**Last Updated**: February 6, 2025  
**GitHub Account**: habeneyasu  
**Repository**: https://github.com/habeneyasu/chimera-factory
