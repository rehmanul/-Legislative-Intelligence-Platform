# Agent Runner Cockpit

**Simple HTML interface to execute Python agents directly - No API required!**

## Quick Start

### Option 1: Double-Click (Easiest)

1. **Double-click** `START_AGENT_COCKPIT.bat`
2. Browser opens automatically
3. Click "Run Agent" buttons to execute agents

### Option 2: Manual Start

1. **Start the server:**
   ```powershell
   cd agent-orchestrator/dashboards
   python server.py
   ```

2. **Open the HTML file:**
   - Open `agent_runner_cockpit.html` in your browser
   - Or navigate to: `file:///path/to/agent_runner_cockpit.html`

## How It Works

```
┌─────────────────┐
│  HTML Cockpit   │  ← You interact here
│  (agent_runner  │
│   _cockpit.html) │
└────────┬────────┘
         │ HTTP (localhost:9000)
         ▼
┌─────────────────┐
│  Python Server  │  ← Executes agents
│  (server.py)    │
└────────┬────────┘
         │ subprocess.run()
         ▼
┌─────────────────┐
│  Agent Scripts  │  ← Your Python agents
│  (agents/*.py)  │
└─────────────────┘
```

**No API, no complex setup - just HTML + Python!**

## Features

- ✅ **List all agents** from registry or directory scan
- ✅ **Filter by type** (Intelligence, Drafting, Execution, Learning)
- ✅ **Filter by status** (Running, Idle, Waiting Review, Blocked)
- ✅ **Search agents** by name or description
- ✅ **Execute agents** with one click
- ✅ **View output** in real-time
- ✅ **No API required** - direct Python execution

## Server Endpoints

The server provides these endpoints:

- `GET /health` - Check server status
- `GET /agents` - List all available agents
- `POST /run` - Execute an agent
  ```json
  {
    "agent_id": "intel_signal_scan_pre_evt"
  }
  ```

## Agent Execution

When you click "Run Agent":

1. Server finds the agent file (`agents/{agent_id}.py`)
2. Executes it with `python agents/{agent_id}.py`
3. Captures stdout, stderr, and return code
4. Returns results to the HTML cockpit
5. Shows output in the panel below

## Troubleshooting

### Server Not Connected

**Problem:** Status shows "Server: Not Connected"

**Solution:**
```powershell
cd agent-orchestrator/dashboards
python server.py
```

### Agent Not Found

**Problem:** "Agent file not found"

**Solution:**
- Check that `agents/{agent_id}.py` exists
- Agent ID must match filename exactly
- Check subdirectories (agents may be in subfolders)

### Port Already in Use

**Problem:** "Address already in use"

**Solution:**
- Change port in `server.py` (line with `port = 9000`)
- Or stop the other process using port 9000

## File Structure

```
agent-orchestrator/dashboards/
├── agent_runner_cockpit.html  ← HTML interface
├── server.py                   ← Python HTTP server
├── START_AGENT_COCKPIT.bat    ← Launcher script
└── AGENT_COCKPIT_README.md     ← This file
```

## Why This Approach?

**You said:** "Agents are Python scripts anyway, why do I need an API?"

**This solution:**
- ✅ No API layer - direct Python execution
- ✅ HTML-only interface (follows HTML-only rules)
- ✅ Simple HTTP server (just executes scripts)
- ✅ Works locally, no deployment needed
- ✅ Easy to understand and modify

**Perfect for local development and testing!**

---

**Last Updated:** 2026-01-20
