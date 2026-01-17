"""
Script: review_server.py
Intent: dev-only server

Reads:
- agent-orchestrator/artifacts/ (serves static files)
- agent-orchestrator/artifacts/reviews/append__artifact_reviews.out.json

Writes:
- agent-orchestrator/artifacts/reviews/append__artifact_reviews.out.json (append-only)
- agent-orchestrator/artifacts/reviews/aggregate__review_brief.out.json
- agent-orchestrator/artifacts/reviews/aggregate__review_brief.md

Purpose: Local dev server for artifact review workflow
- Serves ARTIFACT_INDEX.html and artifacts
- Provides API for review decisions
- Generates one-look briefing documents
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from review_schema import (
    ReviewEntry, ReviewLog, create_review_entry, load_review_log,
    save_review_log, append_review, get_latest_status, get_artifacts_by_status,
    get_llm_ready_artifacts, validate_review_entry, SCHEMA_VERSION
)

try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("[ERROR] FastAPI not installed. Run: pip install fastapi uvicorn")
    print("[INFO] Installing now...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn"], check=True)
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn


# Paths
BASE_DIR = Path(__file__).parent.parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
REVIEWS_DIR = ARTIFACTS_DIR / "reviews"
REVIEW_LOG_PATH = REVIEWS_DIR / "append__artifact_reviews.out.json"
BRIEF_JSON_PATH = REVIEWS_DIR / "aggregate__review_brief.out.json"
BRIEF_MD_PATH = REVIEWS_DIR / "aggregate__review_brief.md"

# Ensure directories exist
REVIEWS_DIR.mkdir(parents=True, exist_ok=True)

# FastAPI app
app = FastAPI(
    title="Artifact Review Server",
    description="Local server for artifact review workflow",
    version="1.0.0"
)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API
class ReviewRequest(BaseModel):
    artifact_path: str
    decision: str  # APPROVE, REJECT, REVISE
    reason: str
    reviewer: str = "local_user"
    selected_for_llm: bool = False
    intended_recipient: str = ""
    why_sending: str = ""


class BriefRequest(BaseModel):
    title: str = "Artifact Review Brief"
    description: str = ""
    include_content_excerpts: bool = True
    max_excerpt_length: int = 500


# API Endpoints

@app.get("/")
async def root():
    """Redirect to artifact viewer."""
    return FileResponse(ARTIFACTS_DIR / "ARTIFACT_INDEX.html")


@app.get("/api/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "server": "review_server",
        "version": "1.0.0",
        "schema_version": SCHEMA_VERSION,
        "artifacts_dir": str(ARTIFACTS_DIR),
        "review_log_exists": REVIEW_LOG_PATH.exists()
    }


@app.get("/api/v1/artifacts/index")
async def get_artifact_index():
    """Get comprehensive artifact index with review status."""
    artifacts_data = {
        "intelligence": [],
        "drafting": [],
        "execution": [],
        "learning": [],
        "policy": [],
        "system": [],
        "other": []
    }
    
    # Load review log to get review status
    log = load_review_log(REVIEW_LOG_PATH)
    review_map = {}
    for review in log.reviews:
        latest = get_latest_status(log, review.artifact_path)
        review_map[review.artifact_path] = {
            "state": latest.get("decision", "UNREVIEWED"),
            "reviewed_at": latest.get("reviewed_at"),
            "reviewed_by": latest.get("reviewer")
        }
    
    # Scan artifacts directory (same logic as temporal__generate_artifact_index.py)
    for artifact_dir in sorted(ARTIFACTS_DIR.iterdir()):
        if not artifact_dir.is_dir():
            continue
        
        dir_name = artifact_dir.name
        if dir_name.startswith(".") or dir_name in ["rendered", "codex_reviews", "debug_dashboard", "reviews"]:
            continue
        
        # Categorize by agent type prefix
        category = "other"
        if dir_name.startswith("intel_"):
            category = "intelligence"
        elif dir_name.startswith("draft_"):
            category = "drafting"
        elif dir_name.startswith("execution_"):
            category = "execution"
        elif dir_name.startswith("learning_"):
            category = "learning"
        elif dir_name == "policy":
            category = "policy"
        elif dir_name in ["system_status_snapshot", "review_templates", "development"]:
            category = "system"
        
        # Scan files in directory
        for file_path in sorted(artifact_dir.rglob("*")):
            if file_path.is_dir():
                continue
            
            if file_path.suffix in [".json", ".md", ".txt", ".mmd"]:
                try:
                    file_stat = file_path.stat()
                    relative_path = file_path.relative_to(BASE_DIR)
                    
                    meta = {}
                    artifact_type = None
                    if file_path.suffix == ".json":
                        try:
                            data = json.loads(file_path.read_text(encoding="utf-8"))
                            meta = data.get("_meta", {})
                            artifact_type = meta.get("artifact_type") or meta.get("artifact_name")
                        except:
                            pass
                    
                    # Get review status
                    review_status = review_map.get(str(relative_path).replace("\\", "/"), {
                        "state": "UNREVIEWED",
                        "reviewed_at": None,
                        "reviewed_by": None
                    })
                    
                    artifact_info = {
                        "name": file_path.name,
                        "path": str(relative_path).replace("\\", "/"),
                        "full_path": str(file_path),
                        "directory": dir_name,
                        "size": file_stat.st_size,
                        "modified": datetime.fromtimestamp(file_stat.st_mtime, tz=timezone.utc).isoformat(),
                        "artifact_type": artifact_type or file_path.stem,
                        "meta": meta,
                        "review_status": review_status
                    }
                    
                    artifacts_data[category].append(artifact_info)
                except Exception as e:
                    print(f"Warning: Could not process {file_path}: {e}")
    
    # Also scan root-level files
    for file_path in sorted(ARTIFACTS_DIR.iterdir()):
        if file_path.is_file() and file_path.suffix in [".json", ".md", ".txt", ".mmd", ".html", ".bat"]:
            if file_path.name in ["ARTIFACT_INDEX.html", "ARTIFACT_INDEX.json"]:
                continue
            try:
                file_stat = file_path.stat()
                relative_path = file_path.relative_to(BASE_DIR)
                
                meta = {}
                artifact_type = None
                if file_path.suffix == ".json":
                    try:
                        data = json.loads(file_path.read_text(encoding="utf-8"))
                        meta = data.get("_meta", {})
                        artifact_type = meta.get("artifact_type") or meta.get("artifact_name")
                    except:
                        pass
                
                review_status = review_map.get(str(relative_path).replace("\\", "/"), {
                    "state": "UNREVIEWED",
                    "reviewed_at": None,
                    "reviewed_by": None
                })
                
                artifact_info = {
                    "name": file_path.name,
                    "path": str(relative_path).replace("\\", "/"),
                    "full_path": str(file_path),
                    "directory": "root",
                    "size": file_stat.st_size,
                    "modified": datetime.fromtimestamp(file_stat.st_mtime, tz=timezone.utc).isoformat(),
                    "artifact_type": artifact_type or file_path.stem,
                    "meta": meta,
                    "review_status": review_status
                }
                
                artifacts_data["other"].append(artifact_info)
            except Exception as e:
                print(f"Warning: Could not process {file_path}: {e}")
    
    # Calculate totals
    total = sum(len(artifacts_data[cat]) for cat in artifacts_data.keys())
    
    return {
        "_meta": {
            "generated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "total_artifacts": total,
            "categories": {cat: len(artifacts_data[cat]) for cat in artifacts_data.keys()}
        },
        "artifacts": artifacts_data
    }


@app.get("/api/reviews")
async def get_reviews():
    """Get all reviews."""
    log = load_review_log(REVIEW_LOG_PATH)
    return log.to_dict()


@app.get("/api/reviews/status")
async def get_review_status():
    """Get review status summary."""
    log = load_review_log(REVIEW_LOG_PATH)
    by_status = get_artifacts_by_status(log)
    
    return {
        "total_reviews": len(log.reviews),
        "unique_artifacts": len(set(r.artifact_path for r in log.reviews)),
        "by_status": {k: len(v) for k, v in by_status.items()},
        "approved_count": len(by_status["APPROVE"]),
        "rejected_count": len(by_status["REJECT"]),
        "revise_count": len(by_status["REVISE"]),
        "llm_ready_count": len(get_llm_ready_artifacts(log))
    }


@app.get("/api/reviews/artifact/{artifact_path:path}")
async def get_artifact_reviews(artifact_path: str):
    """Get reviews for a specific artifact."""
    log = load_review_log(REVIEW_LOG_PATH)
    
    matching = [r.to_dict() for r in log.reviews if r.artifact_path == artifact_path]
    latest = get_latest_status(log, artifact_path)
    
    return {
        "artifact_path": artifact_path,
        "latest_status": latest,
        "review_history": matching
    }


@app.post("/api/reviews")
async def create_review(request: ReviewRequest):
    """Create a new review."""
    # Validate decision
    if request.decision not in ["APPROVE", "REJECT", "REVISE"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid decision: {request.decision}. Must be APPROVE, REJECT, or REVISE"
        )
    
    # Create review entry
    entry = create_review_entry(
        artifact_path=request.artifact_path,
        decision=request.decision,
        reason=request.reason,
        reviewer=request.reviewer,
        selected_for_llm=request.selected_for_llm,
        intended_recipient=request.intended_recipient,
        why_sending=request.why_sending,
        base_dir=BASE_DIR
    )
    
    # Validate entry
    is_valid, errors = validate_review_entry(entry.to_dict())
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Validation errors: {errors}")
    
    # Append to log
    success = append_review(REVIEW_LOG_PATH, entry)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save review")
    
    return {
        "status": "created",
        "review_id": entry.review_id,
        "artifact_path": entry.artifact_path,
        "decision": entry.decision
    }


@app.get("/api/reviews/llm-ready")
async def get_llm_ready():
    """Get artifacts ready for LLM handoff."""
    log = load_review_log(REVIEW_LOG_PATH)
    ready = get_llm_ready_artifacts(log)
    
    return {
        "count": len(ready),
        "artifacts": [r.to_dict() for r in ready]
    }


@app.post("/api/brief")
async def generate_brief(request: BriefRequest):
    """Generate one-look briefing document."""
    log = load_review_log(REVIEW_LOG_PATH)
    ready = get_llm_ready_artifacts(log)
    
    if not ready:
        raise HTTPException(
            status_code=400,
            detail="No artifacts are approved and selected for LLM. Review some artifacts first."
        )
    
    # Build brief data
    brief_data = {
        "_meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "schema_version": SCHEMA_VERSION,
            "title": request.title,
            "description": request.description,
            "artifact_count": len(ready)
        },
        "summary": {
            "what_is_being_sent": f"{len(ready)} artifacts selected for LLM review",
            "recipients": list(set(r.intended_recipient for r in ready if r.intended_recipient)),
            "total_artifacts": len(ready)
        },
        "artifacts": []
    }
    
    # Add artifact details
    for review in ready:
        artifact_path = BASE_DIR / review.artifact_path
        
        # Read content excerpt if requested
        content_excerpt = ""
        if request.include_content_excerpts and artifact_path.exists():
            try:
                content = artifact_path.read_text(encoding="utf-8")
                if len(content) > request.max_excerpt_length:
                    content_excerpt = content[:request.max_excerpt_length] + "..."
                else:
                    content_excerpt = content
            except Exception:
                content_excerpt = "[Could not read content]"
        
        brief_data["artifacts"].append({
            "path": review.artifact_path,
            "what": f"Artifact: {Path(review.artifact_path).name}",
            "why_sending": review.why_sending or "No reason specified",
            "where_going": review.intended_recipient or "Not specified",
            "how_getting_there": "Manual copy/paste or API call",
            "content_hash": review.artifact_sha256,
            "reviewed_at": review.reviewed_at,
            "reviewer": review.reviewer,
            "approval_reason": review.reason,
            "content_excerpt": content_excerpt if request.include_content_excerpts else "[Excerpts disabled]"
        })
    
    # Save JSON brief
    BRIEF_JSON_PATH.write_text(json.dumps(brief_data, indent=2), encoding="utf-8")
    
    # Generate Markdown brief
    md_content = generate_markdown_brief(brief_data)
    BRIEF_MD_PATH.write_text(md_content, encoding="utf-8")
    
    return {
        "status": "generated",
        "json_path": str(BRIEF_JSON_PATH),
        "md_path": str(BRIEF_MD_PATH),
        "artifact_count": len(ready)
    }


def generate_markdown_brief(brief_data: Dict[str, Any]) -> str:
    """Generate human-readable Markdown brief."""
    meta = brief_data["_meta"]
    summary = brief_data["summary"]
    artifacts = brief_data["artifacts"]
    
    md = f"""# {meta['title']}

**Generated:** {meta['generated_at']}  
**Total Artifacts:** {meta['artifact_count']}

{meta.get('description', '')}

---

## Summary

- **What is being sent:** {summary['what_is_being_sent']}
- **Recipients:** {', '.join(summary['recipients']) or 'Not specified'}
- **Total artifacts:** {summary['total_artifacts']}

---

## Artifact Details

"""
    
    for i, artifact in enumerate(artifacts, 1):
        md += f"""### {i}. {artifact['what']}

| Question | Answer |
|----------|--------|
| **What** | `{artifact['path']}` |
| **Why sending** | {artifact['why_sending']} |
| **Where going** | {artifact['where_going']} |
| **How getting there** | {artifact['how_getting_there']} |
| **Content hash** | `{artifact['content_hash'][:16]}...` |
| **Reviewed at** | {artifact['reviewed_at']} |
| **Reviewer** | {artifact['reviewer']} |
| **Approval reason** | {artifact['approval_reason']} |

"""
        if artifact.get('content_excerpt') and artifact['content_excerpt'] != "[Excerpts disabled]":
            md += f"""<details>
<summary>Content Excerpt</summary>

```
{artifact['content_excerpt']}
```

</details>

"""
    
    md += """---

## Approval Log

This document was generated from the review log at:
`artifacts/reviews/append__artifact_reviews.out.json`

Each artifact listed above has been:
1. Reviewed by a human
2. Marked as APPROVED
3. Selected for LLM handoff
4. Documented with reason and recipient

---

*End of Brief*
"""
    
    return md


@app.get("/api/brief")
async def get_brief():
    """Get the latest generated brief."""
    if not BRIEF_JSON_PATH.exists():
        raise HTTPException(status_code=404, detail="No brief generated yet. POST to /api/brief first.")
    
    return json.loads(BRIEF_JSON_PATH.read_text(encoding="utf-8"))


@app.get("/api/brief/md")
async def get_brief_md():
    """Get the latest generated brief as Markdown."""
    if not BRIEF_MD_PATH.exists():
        raise HTTPException(status_code=404, detail="No brief generated yet. POST to /api/brief first.")
    
    return HTMLResponse(
        content=f"<pre>{BRIEF_MD_PATH.read_text(encoding='utf-8')}</pre>",
        media_type="text/html"
    )


# Mount static files for artifacts
app.mount("/artifacts", StaticFiles(directory=str(ARTIFACTS_DIR)), name="artifacts")


def main():
    """Run the review server."""
    print("[INFO] Starting Artifact Review Server...")
    print(f"[INFO] Artifacts directory: {ARTIFACTS_DIR}")
    print(f"[INFO] Review log: {REVIEW_LOG_PATH}")
    print("")
    print("[INFO] Endpoints:")
    print("  GET  /                     - Artifact viewer")
    print("  GET  /api/health           - Health check")
    print("  GET  /api/v1/artifacts/index - Artifact catalog with review status")
    print("  GET  /api/reviews          - All reviews")
    print("  GET  /api/reviews/status   - Review status summary")
    print("  POST /api/reviews          - Create review")
    print("  GET  /api/reviews/llm-ready - Artifacts ready for LLM")
    print("  POST /api/brief            - Generate one-look brief")
    print("  GET  /api/brief            - Get latest brief (JSON)")
    print("  GET  /api/brief/md         - Get latest brief (Markdown)")
    print("")
    print("[INFO] Open http://localhost:8080 in your browser")
    print("[INFO] Press Ctrl+C to stop")
    print("")
    
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")


if __name__ == "__main__":
    main()
