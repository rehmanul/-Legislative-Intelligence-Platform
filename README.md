# Legislative Intelligence Platform

A production-ready orchestration system for managing legislative intelligence workflows with AI agents, human review gates, and real-time dashboards.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Legislative Intelligence Platform             │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React/Vite)          │  Backend (FastAPI/Python)     │
│  ├── Dashboard UI               │  ├── REST API Endpoints       │
│  ├── Real-time Polling          │  ├── File Upload Pipeline     │
│  ├── Agent Swarm Viz            │  ├── Agent Execution Engine   │
│  └── Review Queue UI            │  └── Review Gate Management   │
├─────────────────────────────────────────────────────────────────┤
│                      Data Layer (JSON Files)                     │
│  ├── agent-registry.json        │  ├── HR_PRE_queue.json        │
│  ├── execution-status.json      │  ├── kpi_state.json           │
│  └── artifacts/                 │  └── audit-log.jsonl          │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **6-Stage Legislative Spine**: PRE_EVT → INTRO_EVT → COMM_EVT → FLOOR_EVT → CONF_EVT → ENACT_EVT
- **Agent Swarms**: Intelligence, Drafting, Execution, and ASK agents
- **Human Review Gates**: HR_PRE, HR_INTRO, HR_COMM for human oversight
- **Real-time Dashboard**: Live KPI metrics, agent status, and execution tracking
- **File Upload Pipeline**: Upload documents → Auto-spawn agents → Generate artifacts

## Quick Start

### Local Development

```bash
# Backend
cd agent-orchestrator
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8001

# Frontend (separate terminal)
cd agent-orchestrator/frontend
npm install
npm run dev
```

### Production Deployment (Render)

1. Push to GitHub
2. Create new Blueprint on [Render Dashboard](https://dashboard.render.com/blueprints)
3. Select this repository - Render auto-detects `render.yaml`
4. Both services deploy on free tier

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/snapshot` | Dashboard polling data |
| `GET /api/v1/registry/agents` | Agent swarm status |
| `GET /api/v1/review/queues` | Human review queues |
| `POST /api/v1/upload` | File upload pipeline |
| `POST /api/v1/review/{gate}/{id}/approve` | Approve review item |

## Environment Variables

```bash
# Backend
ENVIRONMENT=production
PYTHONUNBUFFERED=1

# Frontend (build-time)
VITE_API_URL=https://your-backend.onrender.com
```

## License

MIT
