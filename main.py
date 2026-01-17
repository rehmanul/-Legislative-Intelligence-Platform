"""
Legislative Intelligence Platform - Production API
The Ultimate Orchestration Specialist

This API serves real data from the orchestration system's JSON files,
enabling the dashboard to display live agent status, review queues,
KPIs, and legislative state.
"""

import os
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Literal
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn


# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
REVIEW_DIR = BASE_DIR / "review"
EXECUTION_DIR = BASE_DIR / "execution"
METRICS_DIR = BASE_DIR / "metrics"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
REGISTRY_DIR = BASE_DIR / "registry"
STATE_DIR = BASE_DIR / "state"
GUIDANCE_DIR = BASE_DIR / "guidance"
DASHBOARDS_DIR = BASE_DIR / "dashboards"

# Ensure directories exist
for d in [DATA_DIR, REVIEW_DIR, EXECUTION_DIR, METRICS_DIR, 
          ARTIFACTS_DIR, REGISTRY_DIR, STATE_DIR]:
    d.mkdir(exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════
# Models
# ═══════════════════════════════════════════════════════════════════════════

class ReviewDecision(BaseModel):
    decision: Literal["APPROVED", "REJECTED"]
    decision_by: str
    decision_rationale: Optional[str] = None


class StateTransition(BaseModel):
    new_state: Literal["PRE_EVT", "INTRO_EVT", "COMM_EVT", "FLOOR_EVT", "FINAL_EVT", "IMPL_EVT"]
    source: Literal["external", "human-confirmation"]
    rationale: Optional[str] = None


class AgentSpawnRequest(BaseModel):
    agent_type: Literal["Intelligence", "Drafting", "Execution", "Learning"]
    scope: str
    phase: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════

def load_json(path: Path, default: Any = None) -> Any:
    """Load JSON file with fallback to default"""
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {path}: {e}")
    return default if default is not None else {}


def save_json(path: Path, data: Any) -> None:
    """Save JSON file with pretty printing"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def now_iso() -> str:
    """Get current ISO timestamp"""
    return datetime.now(timezone.utc).isoformat()


def get_legislative_state() -> Dict:
    """Get current legislative state from execution status or state file"""
    # Try execution status first
    exec_status = load_json(EXECUTION_DIR / "execution-status.json")
    if exec_status:
        return {
            "current_state": exec_status.get("legislative_state", "PRE_EVT"),
            "current_phase": exec_status.get("_meta", {}).get("current_phase", "UNKNOWN"),
            "phases": exec_status.get("phases", {}),
            "execution_status": exec_status.get("execution_status", "UNKNOWN"),
            "pause_reason": exec_status.get("pause_reason"),
            "next_action": exec_status.get("next_action"),
        }
    
    # Fallback to state file
    state_data = load_json(STATE_DIR / "legislative-state.json")
    return {
        "current_state": state_data.get("current_state", "PRE_EVT"),
        "state_history": state_data.get("state_history", []),
    }


# ═══════════════════════════════════════════════════════════════════════════
# App Setup
# ═══════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize state files from templates if they don't exist"""
    import shutil
    
    # 1. Initialize Registry
    registry_path = REGISTRY_DIR / "agent-registry.json"
    registry_template = REGISTRY_DIR / "agent-registry.template.json"
    if not registry_path.exists() and registry_template.exists():
        shutil.copy(registry_template, registry_path)
    # Fallback backup check (legacy)
    elif not registry_path.exists():
        backup_path = BASE_DIR.parent.parent / "agent-orchestrator" / "registry" / "agent-registry.json.backup"
        if backup_path.exists():
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(backup_path, registry_path)

    # 2. Initialize Execution Status
    execution_path = EXECUTION_DIR / "execution-status.json"
    execution_template = EXECUTION_DIR / "execution-status.template.json"
    if not execution_path.exists() and execution_template.exists():
        shutil.copy(execution_template, execution_path)

    # 3. Initialize Review Queues
    # Only initializing HR_PRE which is critical, others are auto-created by logic if missing
    hr_pre_path = REVIEW_DIR / "HR_PRE_queue.json"
    hr_pre_template = REVIEW_DIR / "HR_PRE_queue.template.json"
    if not hr_pre_path.exists() and hr_pre_template.exists():
        shutil.copy(hr_pre_template, hr_pre_path)
    
    yield


app = FastAPI(
    title="Legislative Intelligence Platform",
    description="The Ultimate Orchestration Specialist - Production API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════
# Root & Health
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def root():
    """API documentation page"""
    state = get_legislative_state()
    return f"""
    <html>
    <head>
        <title>Legislative Intelligence Platform</title>
        <style>
            body {{ font-family: 'Inter', sans-serif; background: #0a0d12; color: #e0e0e0; 
                   max-width: 900px; margin: 50px auto; padding: 20px; }}
            h1 {{ background: linear-gradient(135deg, #00d4ff, #7b61ff); 
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .state {{ background: #1a1a2e; padding: 20px; border-radius: 12px; 
                     border-left: 4px solid #00d4ff; margin: 20px 0; }}
            .endpoint {{ background: #151a22; padding: 12px 16px; margin: 8px 0; 
                        border-radius: 8px; font-family: monospace; }}
            .get {{ border-left: 3px solid #00ff88; }}
            .post {{ border-left: 3px solid #ffaa00; }}
            code {{ color: #00d4ff; }}
            a {{ color: #00d4ff; }}
        </style>
    </head>
    <body>
        <h1>🎯 Legislative Intelligence Platform</h1>
        <p>The Ultimate Orchestration Specialist - Production API</p>
        
        <div class="state">
            <strong>Current State:</strong> <code>{state.get('current_state', 'UNKNOWN')}</code><br>
            <strong>Phase:</strong> <code>{state.get('current_phase', 'UNKNOWN')}</code><br>
            <strong>Status:</strong> <code>{state.get('execution_status', 'UNKNOWN')}</code>
        </div>
        
        <h2>📊 Core Endpoints</h2>
        <div class="endpoint get"><strong>GET</strong> <code>/health</code></div>
        <div class="endpoint get"><strong>GET</strong> <code>/api/v1/registry/agents</code> - Agent swarms</div>
        <div class="endpoint get"><strong>GET</strong> <code>/api/v1/state/current</code> - Legislative state</div>
        <div class="endpoint get"><strong>GET</strong> <code>/api/v1/review/queues</code> - All HR review gates</div>
        <div class="endpoint get"><strong>GET</strong> <code>/api/v1/kpi/state</code> - KPI metrics</div>
        <div class="endpoint get"><strong>GET</strong> <code>/api/v1/kpi/health</code> - Risk indicators</div>
        <div class="endpoint get"><strong>GET</strong> <code>/api/v1/artifacts</code> - Artifact registry</div>
        <div class="endpoint get"><strong>GET</strong> <code>/api/v1/execution/status</code> - Execution status</div>
        
        <h2>🔧 Actions</h2>
        <div class="endpoint post"><strong>POST</strong> <code>/api/v1/review/{{gate}}/{{review_id}}/approve</code></div>
        <div class="endpoint post"><strong>POST</strong> <code>/api/v1/review/{{gate}}/{{review_id}}/reject</code></div>
        <div class="endpoint post"><strong>POST</strong> <code>/api/v1/state/transition</code></div>
        
        <p><a href="/docs">📚 Interactive API Documentation (Swagger)</a></p>
        <p><a href="http://localhost:5173">🖥️ Dashboard UI</a></p>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """System health check with component status"""
    state = get_legislative_state()
    registry = load_json(REGISTRY_DIR / "agent-registry.json", {"agents": []})
    kpi = load_json(METRICS_DIR / "kpi_state.json", {})
    
    return {
        "status": "healthy",
        "timestamp": now_iso(),
        "service": "legislative-intelligence-platform",
        "legislative_state": state.get("current_state", "UNKNOWN"),
        "components": {
            "registry": bool(registry.get("agents")),
            "execution": (EXECUTION_DIR / "execution-status.json").exists(),
            "review_queues": (REVIEW_DIR / "HR_PRE_queue.json").exists(),
            "kpi_metrics": bool(kpi.get("metrics")),
        }
    }


# ═══════════════════════════════════════════════════════════════════════════
# Agent Registry
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/registry/agents")
async def get_agent_registry(
    swarm: Optional[str] = Query(None, description="Filter by agent type: Intelligence, Drafting, Execution, Learning"),
    status: Optional[str] = Query(None, description="Filter by status: RUNNING, WAITING_REVIEW, BLOCKED, RETIRED")
):
    """Get agent registry with swarm grouping"""
    registry = load_json(REGISTRY_DIR / "agent-registry.json", {"_meta": {}, "agents": []})
    agents = registry.get("agents", [])
    meta = registry.get("_meta", {})
    
    # Apply filters
    if swarm:
        agents = [a for a in agents if a.get("agent_type", "").lower() == swarm.lower()]
    if status:
        agents = [a for a in agents if a.get("status", "").upper() == status.upper()]
    
    # Group by swarm
    swarms = {
        "Intelligence": {"agents": [], "running": 0, "waiting_review": 0, "blocked": 0, "retired": 0},
        "Drafting": {"agents": [], "running": 0, "waiting_review": 0, "blocked": 0, "retired": 0},
        "Execution": {"agents": [], "running": 0, "waiting_review": 0, "blocked": 0, "retired": 0},
        "Learning": {"agents": [], "running": 0, "waiting_review": 0, "blocked": 0, "retired": 0},
    }
    
    for agent in agents:
        agent_type = agent.get("agent_type", "Unknown")
        if agent_type in swarms:
            swarms[agent_type]["agents"].append(agent)
            status_key = agent.get("status", "").lower().replace(" ", "_")
            if status_key in swarms[agent_type]:
                swarms[agent_type][status_key] += 1
    
    return {
        "_meta": meta,
        "total_agents": len(registry.get("agents", [])),
        "filtered_count": len(agents),
        "swarms": swarms,
        "agents": agents
    }


# ═══════════════════════════════════════════════════════════════════════════
# Legislative State
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/state/current")
async def get_current_state():
    """Get current legislative state and permitted agent classes"""
    state = get_legislative_state()
    current = state.get("current_state", "PRE_EVT")
    
    # Define permitted agent classes per state
    state_permissions = {
        "PRE_EVT": ["intelligence", "drafting"],
        "INTRO_EVT": ["intelligence", "drafting"],
        "COMM_EVT": ["intelligence", "drafting", "execution"],
        "FLOOR_EVT": ["intelligence", "execution"],
        "FINAL_EVT": ["intelligence", "execution", "learning"],
        "IMPL_EVT": ["learning"],
    }
    
    # Define valid transitions
    valid_transitions = {
        "PRE_EVT": ["INTRO_EVT"],
        "INTRO_EVT": ["COMM_EVT"],
        "COMM_EVT": ["FLOOR_EVT"],
        "FLOOR_EVT": ["FINAL_EVT"],
        "FINAL_EVT": ["IMPL_EVT"],
        "IMPL_EVT": [],
    }
    
    return {
        "current_state": current,
        "current_phase": state.get("current_phase"),
        "execution_status": state.get("execution_status"),
        "pause_reason": state.get("pause_reason"),
        "next_action": state.get("next_action"),
        "permitted_agent_classes": state_permissions.get(current, []),
        "valid_transitions": valid_transitions.get(current, []),
        "phases": state.get("phases", {}),
    }


@app.post("/api/v1/state/transition")
async def transition_state(request: StateTransition):
    """Transition legislative state (requires human confirmation or external source)"""
    state_file = STATE_DIR / "legislative-state.json"
    state_data = load_json(state_file, {
        "current_state": "PRE_EVT",
        "state_history": []
    })
    
    current = state_data.get("current_state", "PRE_EVT")
    
    # Validate transition
    valid_transitions = {
        "PRE_EVT": ["INTRO_EVT"],
        "INTRO_EVT": ["COMM_EVT"],
        "COMM_EVT": ["FLOOR_EVT"],
        "FLOOR_EVT": ["FINAL_EVT"],
        "FINAL_EVT": ["IMPL_EVT"],
        "IMPL_EVT": [],
    }
    
    if request.new_state not in valid_transitions.get(current, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from {current} to {request.new_state}. Valid transitions: {valid_transitions.get(current, [])}"
        )
    
    # Record transition
    state_data["state_history"].append({
        "from_state": current,
        "to_state": request.new_state,
        "source": request.source,
        "rationale": request.rationale,
        "timestamp": now_iso()
    })
    state_data["current_state"] = request.new_state
    
    save_json(state_file, state_data)
    
    return {
        "success": True,
        "previous_state": current,
        "new_state": request.new_state,
        "transition_source": request.source
    }


# ═══════════════════════════════════════════════════════════════════════════
# Human Review Queues
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/review/queues")
async def get_review_queues():
    """Get all human review gate queues"""
    gates = ["HR_PRE", "HR_LANG", "HR_MSG", "HR_RELEASE"]
    result = {}
    
    for gate in gates:
        queue_file = REVIEW_DIR / f"{gate}_queue.json"
        queue_data = load_json(queue_file, {"_meta": {}, "pending_reviews": [], "review_history": []})
        
        pending = queue_data.get("pending_reviews", [])
        # Filter to only truly pending items
        truly_pending = [r for r in pending if not r.get("decision")]
        
        result[gate] = {
            "gate": gate,
            "display_name": queue_data.get("_meta", {}).get("display_name", gate),
            "description": queue_data.get("_meta", {}).get("description", ""),
            "status": queue_data.get("_meta", {}).get("status", "UNKNOWN"),
            "pending_count": len(truly_pending),
            "total_items": len(pending),
            "pending_reviews": truly_pending[:10],  # Limit to first 10
            "history_count": len(queue_data.get("review_history", []))
        }
    
    # Summary stats
    total_pending = sum(q["pending_count"] for q in result.values())
    
    return {
        "timestamp": now_iso(),
        "total_pending": total_pending,
        "gates": result
    }


@app.get("/api/v1/review/{gate}")
async def get_review_queue(gate: str):
    """Get specific review gate queue"""
    gate = gate.upper()
    if not gate.startswith("HR_"):
        gate = f"HR_{gate}"
    
    queue_file = REVIEW_DIR / f"{gate}_queue.json"
    if not queue_file.exists():
        raise HTTPException(status_code=404, detail=f"Review gate {gate} not found")
    
    queue_data = load_json(queue_file)
    return queue_data


@app.post("/api/v1/review/{gate}/{review_id}/approve")
async def approve_review(gate: str, review_id: str, decision: ReviewDecision):
    """Approve a review item"""
    decision.decision = "APPROVED"
    return await process_review_decision(gate, review_id, decision)


@app.post("/api/v1/review/{gate}/{review_id}/reject")
async def reject_review(gate: str, review_id: str, decision: ReviewDecision):
    """Reject a review item"""
    decision.decision = "REJECTED"
    return await process_review_decision(gate, review_id, decision)


async def process_review_decision(gate: str, review_id: str, decision: ReviewDecision):
    """Process a review decision (approve or reject)"""
    gate = gate.upper()
    if not gate.startswith("HR_"):
        gate = f"HR_{gate}"
    
    queue_file = REVIEW_DIR / f"{gate}_queue.json"
    if not queue_file.exists():
        raise HTTPException(status_code=404, detail=f"Review gate {gate} not found")
    
    queue_data = load_json(queue_file)
    pending = queue_data.get("pending_reviews", [])
    
    # Find the review item
    item_index = None
    for i, item in enumerate(pending):
        if item.get("review_id") == review_id:
            item_index = i
            break
    
    if item_index is None:
        raise HTTPException(status_code=404, detail=f"Review ID {review_id} not found in {gate}")
    
    # Update the item
    item = pending[item_index]
    item["decision"] = decision.decision
    item["decision_at"] = now_iso()
    item["decision_by"] = decision.decision_by
    item["decision_rationale"] = decision.rationale
    item["status"] = decision.decision
    
    # Move to history if approved/rejected
    history = queue_data.setdefault("review_history", [])
    history.append(item)
    
    # Remove from pending
    pending.pop(item_index)
    
    save_json(queue_file, queue_data)
    
    return {
        "success": True,
        "gate": gate,
        "review_id": review_id,
        "decision": decision.decision,
        "artifact": item.get("artifact_path")
    }


# ═══════════════════════════════════════════════════════════════════════════
# Execution Status
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/execution/status")
async def get_execution_status():
    """Get execution phase status"""
    exec_status = load_json(EXECUTION_DIR / "execution-status.json")
    if not exec_status:
        return {
            "status": "not_initialized",
            "message": "No execution status found"
        }
    
    return exec_status


# ═══════════════════════════════════════════════════════════════════════════
# KPI Metrics
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/kpi/state")
async def get_kpi_state():
    """Get full KPI state metrics"""
    kpi_data = load_json(METRICS_DIR / "kpi_state.json")
    if not kpi_data:
        return {"status": "not_initialized", "metrics": {}}
    
    return kpi_data


@app.get("/api/v1/kpi/health")
async def get_kpi_health():
    """Get KPI health indicators and risk flags"""
    kpi_data = load_json(METRICS_DIR / "kpi_state.json", {})
    metrics = kpi_data.get("metrics", {})
    
    risk_indicators = metrics.get("risk_indicators", {})
    operational = metrics.get("operational", {})
    system_health = metrics.get("system_health", {})
    
    # Determine overall health
    active_risks = [k for k, v in risk_indicators.items() if v]
    if len(active_risks) >= 3:
        overall = "critical"
    elif len(active_risks) >= 1:
        overall = "degraded"
    else:
        overall = "healthy"
    
    return {
        "overall_status": overall,
        "active_risks": active_risks,
        "risk_count": len(active_risks),
        "risk_indicators": risk_indicators,
        "conversion_rate": operational.get("conversion_rate", 0),
        "dependency_satisfaction": operational.get("dependency_satisfaction", 100),
        "state_velocity": operational.get("state_velocity", {}),
        "override_frequency": system_health.get("override_frequency", 0),
    }


# ═══════════════════════════════════════════════════════════════════════════
# Artifacts
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/artifacts")
async def get_artifacts():
    """Get artifact registry with flow status"""
    artifacts = []
    
    # Scan artifacts directory
    if ARTIFACTS_DIR.exists():
        for artifact_dir in ARTIFACTS_DIR.iterdir():
            if artifact_dir.is_dir():
                for json_file in artifact_dir.glob("*.json"):
                    try:
                        data = load_json(json_file)
                        meta = data.get("_meta", {})
                        artifacts.append({
                            "name": json_file.stem,
                            "path": str(json_file.relative_to(BASE_DIR)),
                            "category": artifact_dir.name,
                            "type": meta.get("artifact_type", data.get("artifact_type", "UNKNOWN")),
                            "generated_at": meta.get("generated_at", meta.get("created_at")),
                            "status": meta.get("status", "SPECULATIVE"),
                            "requires_review": meta.get("requires_review", False),
                        })
                    except Exception:
                        pass
    
    # Calculate flow metrics
    speculative = len([a for a in artifacts if a["status"] == "SPECULATIVE"])
    actionable = len([a for a in artifacts if a["status"] == "ACTIONABLE"])
    in_review = len([a for a in artifacts if a.get("requires_review")])
    
    return {
        "total": len(artifacts),
        "speculative": speculative,
        "actionable": actionable,
        "in_review": in_review,
        "artifacts": artifacts[:50]  # Limit response size
    }


# ═══════════════════════════════════════════════════════════════════════════
# Snapshot (for dashboard polling)
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/snapshot")
async def get_snapshot():
    """Get compiled snapshot for dashboard (matches snapshot-compiler.js output)"""
    # Get all data
    registry = load_json(REGISTRY_DIR / "agent-registry.json", {"agents": []})
    kpi = load_json(METRICS_DIR / "kpi_state.json", {})
    exec_status = load_json(EXECUTION_DIR / "execution-status.json", {})
    
    agents = registry.get("agents", [])
    metrics = kpi.get("metrics", {})
    
    # Compile agent swarms
    def compile_swarm(agent_type: str) -> Dict:
        filtered = [a for a in agents if a.get("agent_type") == agent_type]
        return {
            "total": len(filtered),
            "running": len([a for a in filtered if a.get("status") == "RUNNING"]),
            "waiting_review": len([a for a in filtered if a.get("status") == "WAITING_REVIEW"]),
            "blocked": len([a for a in filtered if a.get("status") == "BLOCKED"]),
            "retired": len([a for a in filtered if a.get("status") == "RETIRED"]),
        }
    
    # Get review pending counts
    review_pending = {}
    for gate in ["HR_PRE", "HR_LANG", "HR_MSG", "HR_RELEASE"]:
        queue = load_json(REVIEW_DIR / f"{gate}_queue.json", {})
        pending = [r for r in queue.get("pending_reviews", []) if not r.get("decision")]
        review_pending[gate] = len(pending)
    
    return {
        "timestamp": now_iso(),
        "heartbeat": "alive",
        "legislative_state": {
            "current": exec_status.get("legislative_state", "PRE_EVT"),
            "phase": exec_status.get("_meta", {}).get("current_phase"),
            "execution_status": exec_status.get("execution_status"),
        },
        "agent_swarms": {
            "intelligence": compile_swarm("Intelligence"),
            "drafting": compile_swarm("Drafting"),
            "execution": compile_swarm("Execution"),
            "learning": compile_swarm("Learning"),
        },
        "review_queues": review_pending,
        "kpis": {
            "conversion_rate": metrics.get("operational", {}).get("conversion_rate", 0),
            "risk_indicators": metrics.get("risk_indicators", {}),
            "state_velocity": metrics.get("operational", {}).get("state_velocity", {}),
        }
    }


# ═══════════════════════════════════════════════════════════════════════════
# PRODUCTION FILE UPLOAD & PROCESSING PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

from fastapi import UploadFile, File, Form, BackgroundTasks
import shutil
import hashlib
from agents.intelligence.generic_intel_agent import GenericIntelligenceAgent

# Create uploads directory
UPLOADS_DIR = ARTIFACTS_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from PDF using PyMuPDF if available, otherwise return placeholder"""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(file_path))
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except ImportError:
        # PyMuPDF not installed - return file info instead
        return f"[PDF file: {file_path.name}, size: {file_path.stat().st_size} bytes. Install PyMuPDF for text extraction: pip install pymupdf]"
    except Exception as e:
        return f"[Error extracting PDF text: {str(e)}]"


def spawn_intelligence_agent(artifact_id: str, artifact_path: str, document_type: str) -> Dict:
    """Spawn an intelligence agent to process the uploaded document"""
    agent_id = f"intel_doc_analysis_{artifact_id}"
    
    agent = {
        "agent_id": agent_id,
        "agent_type": "Intelligence",
        "status": "RUNNING",
        "scope": f"Document analysis for {document_type}",
        "current_task": f"Analyzing uploaded document: {Path(artifact_path).name}",
        "last_heartbeat": now_iso(),
        "risk_level": "LOW",
        "outputs": [],
        "spawned_at": now_iso(),
        "input_artifact": artifact_path,
        "termination_condition": "Analysis complete OR error OR 1-hour timeout"
    }
    
    # Add to registry
    registry_path = REGISTRY_DIR / "agent-registry.json"
    registry = load_json(registry_path, {"_meta": {}, "agents": []})
    registry["agents"].append(agent)
    registry["_meta"]["last_updated"] = now_iso()
    registry["_meta"]["total_agents"] = len(registry["agents"])
    save_json(registry_path, registry)
    
    return agent


def create_review_item(artifact_id: str, artifact_name: str, artifact_type: str, 
                       artifact_path: str, document_summary: str) -> Dict:
    """Create a review item and add to HR_PRE queue"""
    review_id = f"review_{artifact_id}"
    
    review_item = {
        "review_id": review_id,
        "artifact_name": artifact_name,
        "artifact_type": artifact_type,
        "artifact_path": artifact_path,
        "risk_level": "Medium",
        "submitted_by": "upload_processor",
        "submitted_at": now_iso(),
        "review_effort_estimate": "15-30 minutes",
        "document_summary": document_summary[:500] if document_summary else "No summary available",
        "status": "PENDING",
        "decision": None,
        "decision_at": None,
        "decision_by": None,
        "decision_rationale": None
    }
    
    # Add to HR_PRE queue
    queue_path = REVIEW_DIR / "HR_PRE_queue.json"
    queue = load_json(queue_path, {
        "_meta": {
            "gate": "HR_PRE",
            "display_name": "Pre-Event Concept Review",
            "description": "Review uploaded documents before processing",
            "status": "ACTIVE"
        },
        "pending_reviews": [],
        "review_history": []
    })
    
    queue["pending_reviews"].insert(0, review_item)  # Add at beginning
    queue["_meta"]["last_updated"] = now_iso()
    save_json(queue_path, queue)
    
    return review_item


def update_execution_status(artifact_id: str, phase: str = "intelligence"):
    """Update execution status to reflect new processing"""
    exec_path = EXECUTION_DIR / "execution-status.json"
    exec_status = load_json(exec_path, {
        "_meta": {"current_phase": "intelligence"},
        "legislative_state": "PRE_EVT",
        "execution_status": "RUNNING",
        "phases": {
            "intelligence": {"status": "RUNNING"},
            "drafting": {"status": "PENDING"},
            "human_review": {"status": "PENDING"}
        }
    })
    
    exec_status["_meta"]["current_phase"] = phase
    exec_status["_meta"]["last_updated"] = now_iso()
    exec_status["execution_status"] = "RUNNING"
    exec_status["phases"]["intelligence"]["status"] = "RUNNING"
    exec_status["pause_reason"] = None
    exec_status["next_action"] = f"Processing document: {artifact_id}"
    
    save_json(exec_path, exec_status)


def process_uploaded_file(file_path: Path, artifact_id: str, original_filename: str):
    """Background task to process uploaded file"""
    try:
        # Extract text if PDF
        document_text = ""
        if file_path.suffix.lower() == ".pdf":
            document_text = extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() in [".txt", ".md"]:
            document_text = file_path.read_text(encoding="utf-8", errors="ignore")
        elif file_path.suffix.lower() == ".json":
            document_text = json.dumps(load_json(file_path), indent=2)
        
        # Create artifact metadata
        artifact_meta = {
            "_meta": {
                "artifact_id": artifact_id,
                "artifact_type": "UPLOADED_DOCUMENT",
                "original_filename": original_filename,
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "uploaded_at": now_iso(),
                "status": "SPECULATIVE",
                "requires_review": True
            },
            "content_preview": document_text[:2000] if document_text else None,
            "content_length": len(document_text) if document_text else 0
        }
        
        # Save artifact metadata
        meta_path = file_path.with_suffix(file_path.suffix + ".meta.json")
        save_json(meta_path, artifact_meta)
        
        # Spawn intelligence agent registry entry
        agent_entry = spawn_intelligence_agent(artifact_id, str(file_path), file_path.suffix.upper())
        
        # EXECUTE ACTUAL AGENT LOGIC
        print(f"🤖 Spawning Intelligence Agent Process for {artifact_id}...")
        try:
            agent = GenericIntelligenceAgent(workflow_id=artifact_id, artifact_path=str(file_path))
            output_path = agent.main()
            
            if output_path:
                print(f"✅ Agent execution complete. Output: {output_path}")
                
                # Update agent status in registry
                registry_path = REGISTRY_DIR / "agent-registry.json"
                registry = load_json(registry_path)
                for a in registry["agents"]:
                    if a["agent_id"] == agent_entry["agent_id"]:
                        a["status"] = "IDLE"
                        a["current_task"] = "Analysis complete"
                        a["outputs"].append(str(output_path))
                        break
                save_json(registry_path, registry)
                
                # Update review item with analysis summary
                analysis_output = load_json(output_path)
                summary = analysis_output.get("data", {}).get("summary", "Analysis complete")
                
                # Note: In a real system we'd update the specific review item, 
                # but for now we trust the queue matches
                
        except Exception as e:
            print(f"❌ Agent execution failed: {e}")
        
        # Create review item
        create_review_item(
            artifact_id=artifact_id,
            artifact_name=original_filename,
            artifact_type="UPLOADED_DOCUMENT",
            artifact_path=str(file_path),
            document_summary=document_text[:500] if document_text else "Binary file - no text preview"
        )
        
        # Update execution status
        update_execution_status(artifact_id, "intelligence")
        
        print(f"✅ Processed: {original_filename} -> {artifact_id}")
        
    except Exception as e:
        print(f"❌ Error processing {original_filename}: {e}")


@app.post("/api/v1/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type: str = Form(default="artifact")
):
    """
    Production file upload endpoint.
    
    1. Saves file to artifacts/uploads/
    2. Spawns intelligence agent
    3. Creates HR_PRE review item
    4. Updates execution status
    """
    # Generate unique artifact ID
    file_hash = hashlib.md5(f"{file.filename}{now_iso()}".encode()).hexdigest()[:12]
    artifact_id = f"{document_type}_{file_hash}"
    
    # Create safe filename
    safe_filename = file.filename.replace(" ", "_").replace("/", "_").replace("\\", "_")
    file_path = UPLOADS_DIR / f"{artifact_id}_{safe_filename}"
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Process in background
    background_tasks.add_task(process_uploaded_file, file_path, artifact_id, file.filename)
    
    return {
        "success": True,
        "artifact_id": artifact_id,
        "filename": file.filename,
        "saved_path": str(file_path),
        "file_size": file_path.stat().st_size,
        "status": "processing",
        "message": "File uploaded. Intelligence agent spawned. Review item created in HR_PRE queue."
    }


@app.post("/api/v1/upload/batch")
async def upload_batch(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    document_type: str = Form(default="artifact")
):
    """Upload multiple files at once"""
    results = []
    
    for file in files:
        file_hash = hashlib.md5(f"{file.filename}{now_iso()}{len(results)}".encode()).hexdigest()[:12]
        artifact_id = f"{document_type}_{file_hash}"
        
        safe_filename = file.filename.replace(" ", "_").replace("/", "_").replace("\\", "_")
        file_path = UPLOADS_DIR / f"{artifact_id}_{safe_filename}"
        
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            background_tasks.add_task(process_uploaded_file, file_path, artifact_id, file.filename)
            
            results.append({
                "success": True,
                "artifact_id": artifact_id,
                "filename": file.filename,
                "file_size": file_path.stat().st_size
            })
        except Exception as e:
            results.append({
                "success": False,
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "total": len(files),
        "successful": len([r for r in results if r.get("success")]),
        "failed": len([r for r in results if not r.get("success")]),
        "results": results
    }


@app.get("/api/v1/uploads")
async def list_uploads():
    """List all uploaded files"""
    uploads = []
    
    if UPLOADS_DIR.exists():
        for file_path in UPLOADS_DIR.iterdir():
            if file_path.is_file() and not file_path.name.endswith(".meta.json"):
                meta_path = file_path.with_suffix(file_path.suffix + ".meta.json")
                meta = load_json(meta_path, {})
                
                uploads.append({
                    "filename": file_path.name,
                    "artifact_id": meta.get("_meta", {}).get("artifact_id"),
                    "original_filename": meta.get("_meta", {}).get("original_filename", file_path.name),
                    "file_size": file_path.stat().st_size,
                    "uploaded_at": meta.get("_meta", {}).get("uploaded_at"),
                    "status": meta.get("_meta", {}).get("status", "UNKNOWN"),
                    "requires_review": meta.get("_meta", {}).get("requires_review", False)
                })
    
    return {
        "total": len(uploads),
        "uploads_dir": str(UPLOADS_DIR),
        "uploads": sorted(uploads, key=lambda x: x.get("uploaded_at") or "", reverse=True)
    }


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)

