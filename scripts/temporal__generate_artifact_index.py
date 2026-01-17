"""
Script: temporal__generate_artifact_index.py
Intent: temporal

Reads:
- agent-orchestrator/artifacts/ directory

Writes:
- artifacts/ARTIFACT_INDEX.html (comprehensive viewer)
- artifacts/ARTIFACT_INDEX.json (machine-readable index)

Purpose: Generate comprehensive artifact viewer showing all artifacts and locations
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

BASE_DIR = Path(__file__).parent.parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
OUTPUT_DIR = BASE_DIR / "artifacts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def scan_artifacts() -> Dict[str, Any]:
    """Scan artifacts directory and organize by type/phase."""
    artifacts_data = {
        "intelligence": [],
        "drafting": [],
        "execution": [],
        "learning": [],
        "policy": [],
        "system": [],
        "other": []
    }
    
    # First, scan files directly in artifacts directory
    for file_path in sorted(ARTIFACTS_DIR.iterdir()):
        if file_path.is_file() and file_path.suffix in [".json", ".md", ".txt", ".mmd", ".html", ".bat"]:
            # Skip index files
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
                
                artifact_info = {
                    "name": file_path.name,
                    "path": str(relative_path).replace("\\", "/"),
                    "full_path": str(file_path),
                    "directory": "root",
                    "size": file_stat.st_size,
                    "modified": datetime.fromtimestamp(file_stat.st_mtime, tz=timezone.utc).isoformat(),
                    "artifact_type": artifact_type or file_path.stem,
                    "meta": meta
                }
                
                artifacts_data["other"].append(artifact_info)
            except Exception as e:
                print(f"Warning: Could not process {file_path}: {e}")
    
    # Then scan subdirectories
    for artifact_dir in sorted(ARTIFACTS_DIR.iterdir()):
        if not artifact_dir.is_dir():
            continue
        
        dir_name = artifact_dir.name
        
        # Skip certain directories
        if dir_name.startswith(".") or dir_name in ["rendered", "codex_reviews", "debug_dashboard"]:
            continue
        
        # Categorize by agent type prefix or directory name
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
        
        # Scan files in directory (recursively)
        for file_path in sorted(artifact_dir.rglob("*")):
            if file_path.is_dir():
                continue
            
            if file_path.suffix in [".json", ".md", ".txt", ".mmd"]:
                try:
                    file_stat = file_path.stat()
                    relative_path = file_path.relative_to(BASE_DIR)
                    
                    # Try to read _meta if JSON
                    meta = {}
                    artifact_type = None
                    if file_path.suffix == ".json":
                        try:
                            data = json.loads(file_path.read_text(encoding="utf-8"))
                            meta = data.get("_meta", {})
                            artifact_type = meta.get("artifact_type") or meta.get("artifact_name")
                        except:
                            pass
                    
                    artifact_info = {
                        "name": file_path.name,
                        "path": str(relative_path).replace("\\", "/"),
                        "full_path": str(file_path),
                        "directory": dir_name,
                        "size": file_stat.st_size,
                        "modified": datetime.fromtimestamp(file_stat.st_mtime, tz=timezone.utc).isoformat(),
                        "artifact_type": artifact_type or file_path.stem,
                        "meta": meta
                    }
                    
                    artifacts_data[category].append(artifact_info)
                except Exception as e:
                    print(f"Warning: Could not process {file_path}: {e}")
    
    return artifacts_data


def generate_html_viewer(artifacts_data: Dict[str, Any]) -> str:
    """Generate HTML viewer for artifacts."""
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Orchestrator - Complete Artifact Index</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        
        .header {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            color: white;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .header .subtitle {
            opacity: 0.9;
            font-size: 1rem;
        }
        
        .stats {
            background: white;
            padding: 1rem 2rem;
            display: flex;
            gap: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-number {
            font-size: 1.5rem;
            font-weight: bold;
            color: #1e40af;
        }
        
        .stat-label {
            font-size: 0.875rem;
            color: #666;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .tabs {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }
        
        .tab {
            padding: 0.75rem 1.5rem;
            background: white;
            border: 2px solid #e5e7eb;
            border-radius: 8px 8px 0 0;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 500;
        }
        
        .tab:hover {
            background: #eff6ff;
        }
        
        .tab.active {
            background: #3b82f6;
            color: white;
            border-color: #3b82f6;
        }
        
        .tab-content {
            display: none;
            background: white;
            border-radius: 8px;
            padding: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .tab-content.active {
            display: block;
        }
        
        .artifact-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
        }
        
        .artifact-card {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1.5rem;
            transition: all 0.2s;
            background: white;
        }
        
        .artifact-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        
        .artifact-card h3 {
            color: #1e40af;
            margin-bottom: 0.5rem;
            font-size: 1.125rem;
        }
        
        .artifact-card .path {
            font-family: 'Courier New', monospace;
            font-size: 0.875rem;
            color: #666;
            background: #f9fafb;
            padding: 0.5rem;
            border-radius: 4px;
            margin: 0.5rem 0;
            word-break: break-all;
        }
        
        .artifact-card .meta {
            font-size: 0.875rem;
            color: #666;
            margin-top: 0.75rem;
            padding-top: 0.75rem;
            border-top: 1px solid #e5e7eb;
        }
        
        .artifact-card .meta-item {
            margin-bottom: 0.25rem;
        }
        
        .artifact-card .status {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
            margin-top: 0.5rem;
        }
        
        .status.SPECULATIVE {
            background: #fef3c7;
            color: #92400e;
        }
        
        .status.ACTIONABLE {
            background: #d1fae5;
            color: #065f46;
        }
        
        .badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
            margin-right: 0.5rem;
        }
        
        .badge.intelligence {
            background: #dbeafe;
            color: #1e40af;
        }
        
        .badge.drafting {
            background: #fef3c7;
            color: #92400e;
        }
        
        .badge.execution {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .badge.learning {
            background: #e0e7ff;
            color: #3730a3;
        }
        
        .badge.policy {
            background: #ecfdf5;
            color: #065f46;
        }
        
        .badge.system {
            background: #f3f4f6;
            color: #374151;
        }
        
        .search-box {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .search-box:focus {
            outline: none;
            border-color: #3b82f6;
        }
        
        .empty-state {
            text-align: center;
            padding: 3rem;
            color: #666;
        }
        
        .open-file-btn {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 0.5rem;
            margin-right: 0.5rem;
            font-size: 0.875rem;
        }
        
        .open-file-btn:hover {
            background: #2563eb;
        }
        
        .action-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.75rem;
        }
        
        .action-btn {
            background: #10b981;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.875rem;
            flex: 1;
            min-width: 120px;
        }
        
        .action-btn:hover {
            background: #059669;
        }
        
        .action-btn.codex {
            background: #8b5cf6;
        }
        
        .action-btn.codex:hover {
            background: #7c3aed;
        }
        
        .action-btn.debug {
            background: #f59e0b;
        }
        
        .action-btn.debug:hover {
            background: #d97706;
        }
        
        .quick-links {
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid #e5e7eb;
        }
        
        .quick-link {
            display: inline-block;
            margin-right: 1rem;
            margin-bottom: 0.5rem;
            color: #3b82f6;
            text-decoration: none;
            font-size: 0.875rem;
        }
        
        .quick-link:hover {
            text-decoration: underline;
        }
        
        .artifact-card.expanded {
            border-color: #3b82f6;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
        }
        
        .artifact-preview {
            display: none;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 2px solid #e5e7eb;
            max-height: 600px;
            overflow-y: auto;
        }
        
        .artifact-card.expanded .artifact-preview {
            display: block;
        }
        
        .expand-btn {
            background: #e5e7eb;
            color: #374151;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.875rem;
            margin-top: 0.5rem;
            width: 100%;
        }
        
        .expand-btn:hover {
            background: #d1d5db;
        }
        
        .expand-btn.expanded {
            background: #3b82f6;
            color: white;
        }
        
        .preview-content {
            background: #f9fafb;
            padding: 1rem;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.875rem;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 500px;
            overflow-y: auto;
        }
        
        .preview-meta {
            background: #eff6ff;
            padding: 0.75rem;
            border-radius: 4px;
            margin-bottom: 1rem;
            font-size: 0.875rem;
        }
        
        .preview-section {
            margin-bottom: 1rem;
        }
        
        .preview-section-title {
            font-weight: bold;
            color: #1e40af;
            margin-bottom: 0.5rem;
        }
        
        /* Review Controls */
        .review-controls {
            margin-top: 1rem;
            padding: 1rem;
            background: #f8fafc;
            border-radius: 8px;
            border: 2px solid #e2e8f0;
        }
        
        .review-controls.has-status {
            border-color: #94a3b8;
        }
        
        .review-status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }
        
        .review-status-badge.APPROVE {
            background: #dcfce7;
            color: #166534;
        }
        
        .review-status-badge.REJECT {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .review-status-badge.REVISE {
            background: #fef3c7;
            color: #92400e;
        }
        
        .review-status-badge.UNREVIEWED {
            background: #e2e8f0;
            color: #475569;
        }
        
        .review-buttons {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
        }
        
        .review-btn {
            flex: 1;
            padding: 0.5rem 0.75rem;
            border: 2px solid transparent;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            font-size: 0.875rem;
            transition: all 0.2s;
        }
        
        .review-btn.approve {
            background: #dcfce7;
            color: #166534;
            border-color: #86efac;
        }
        
        .review-btn.approve:hover {
            background: #bbf7d0;
        }
        
        .review-btn.reject {
            background: #fee2e2;
            color: #991b1b;
            border-color: #fca5a5;
        }
        
        .review-btn.reject:hover {
            background: #fecaca;
        }
        
        .review-btn.revise {
            background: #fef3c7;
            color: #92400e;
            border-color: #fcd34d;
        }
        
        .review-btn.revise:hover {
            background: #fde68a;
        }
        
        .review-reason {
            width: 100%;
            padding: 0.5rem;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
            font-size: 0.875rem;
            margin-bottom: 0.75rem;
            resize: vertical;
            min-height: 60px;
        }
        
        .review-options {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 0.75rem;
            font-size: 0.875rem;
        }
        
        .review-option {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .review-option input[type="checkbox"] {
            width: 1rem;
            height: 1rem;
        }
        
        .review-option select {
            padding: 0.25rem 0.5rem;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
            font-size: 0.875rem;
        }
        
        .review-submit {
            width: 100%;
            padding: 0.75rem;
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.875rem;
        }
        
        .review-submit:hover {
            background: #2563eb;
        }
        
        .review-submit:disabled {
            background: #94a3b8;
            cursor: not-allowed;
        }
        
        /* Filter bar */
        .filter-bar {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }
        
        .filter-btn {
            padding: 0.5rem 1rem;
            border: 2px solid #e2e8f0;
            border-radius: 6px;
            background: white;
            cursor: pointer;
            font-size: 0.875rem;
            transition: all 0.2s;
        }
        
        .filter-btn:hover {
            border-color: #3b82f6;
        }
        
        .filter-btn.active {
            background: #3b82f6;
            color: white;
            border-color: #3b82f6;
        }
        
        .filter-btn .count {
            display: inline-block;
            padding: 0.125rem 0.5rem;
            background: rgba(0,0,0,0.1);
            border-radius: 9999px;
            font-size: 0.75rem;
            margin-left: 0.5rem;
        }
        
        /* Brief generation */
        .brief-panel {
            background: #eff6ff;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            border: 2px solid #bfdbfe;
        }
        
        .brief-panel h3 {
            margin: 0 0 1rem 0;
            color: #1e40af;
        }
        
        .brief-btn {
            padding: 0.75rem 1.5rem;
            background: #1e40af;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 1rem;
        }
        
        .brief-btn:hover {
            background: #1e3a8a;
        }
        
        .brief-btn:disabled {
            background: #94a3b8;
            cursor: not-allowed;
        }
        
        .server-status {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.875rem;
            margin-left: 1rem;
        }
        
        .server-status.connected {
            background: #dcfce7;
            color: #166534;
        }
        
        .server-status.disconnected {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .server-status .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: currentColor;
        }
        
        /* Review Progress */
        .review-progress {
            background: #f8fafc;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            border: 2px solid #e2e8f0;
        }
        
        .progress-bar-container {
            background: #e2e8f0;
            height: 24px;
            border-radius: 12px;
            overflow: hidden;
            margin: 0.75rem 0;
            position: relative;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #3b82f6, #2563eb);
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 0.75rem;
        }
        
        .progress-stats {
            display: flex;
            gap: 1.5rem;
            margin-top: 0.75rem;
            font-size: 0.875rem;
        }
        
        .progress-stat {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .progress-stat .dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        
        .progress-stat.reviewed .dot { background: #10b981; }
        .progress-stat.pending .dot { background: #f59e0b; }
        .progress-stat.approved .dot { background: #3b82f6; }
        
        /* Unreviewed highlight */
        .artifact-card[data-review-status="UNREVIEWED"] {
            border-left: 4px solid #f59e0b;
            background: linear-gradient(to right, #fef3c7 0%, #ffffff 5%);
        }
        
        .artifact-card[data-review-status="UNREVIEWED"]:hover {
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
        }
        
        /* Review wizard mode */
        .wizard-mode {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: #1e40af;
            color: white;
            padding: 1rem;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        .wizard-controls {
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        
        .wizard-btn {
            padding: 0.5rem 1rem;
            border: 2px solid white;
            border-radius: 6px;
            background: transparent;
            color: white;
            cursor: pointer;
            font-weight: 600;
        }
        
        .wizard-btn:hover {
            background: rgba(255,255,255,0.2);
        }
        
        /* Batch actions */
        .batch-actions {
            background: #eff6ff;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border: 2px solid #bfdbfe;
            display: none;
        }
        
        .batch-actions.active {
            display: block;
        }
        
        .batch-actions-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.75rem;
        }
        
        .batch-select-all {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .batch-actions-buttons {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }
        
        .artifact-card .review-checkbox {
            position: absolute;
            top: 1rem;
            right: 1rem;
            width: 1.25rem;
            height: 1.25rem;
            cursor: pointer;
        }
        
        .artifact-card {
            position: relative;
        }
        
        /* Review quick actions */
        .quick-review-actions {
            display: flex;
            gap: 0.5rem;
            margin-top: 0.75rem;
            flex-wrap: wrap;
        }
        
        .quick-review-btn {
            padding: 0.375rem 0.75rem;
            border: 1px solid;
            border-radius: 4px;
            background: transparent;
            cursor: pointer;
            font-size: 0.75rem;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .quick-review-btn.approve {
            border-color: #10b981;
            color: #10b981;
        }
        
        .quick-review-btn.approve:hover {
            background: #dcfce7;
        }
        
        .quick-review-btn.reject {
            border-color: #ef4444;
            color: #ef4444;
        }
        
        .quick-review-btn.reject:hover {
            background: #fee2e2;
        }
        
        .quick-review-btn.revise {
            border-color: #f59e0b;
            color: #f59e0b;
        }
        
        .quick-review-btn.revise:hover {
            background: #fef3c7;
        }
        
        /* Keyboard shortcuts hint */
        .shortcuts-hint {
            position: fixed;
            bottom: 1rem;
            right: 1rem;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 0.75rem 1rem;
            border-radius: 6px;
            font-size: 0.75rem;
            z-index: 999;
            display: none;
        }
        
        .shortcuts-hint.active {
            display: block;
        }
        
        .shortcuts-hint kbd {
            background: #374151;
            padding: 0.125rem 0.375rem;
            border-radius: 3px;
            font-family: monospace;
        }
        
        /* Loading overlay */
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255,255,255,0.95);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        }
        
        .loading-spinner {
            width: 48px;
            height: 48px;
            border: 4px solid #e5e7eb;
            border-top-color: #3b82f6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Refresh controls */
        .refresh-controls {
            background: #eff6ff;
            padding: 1rem 2rem;
            border-bottom: 2px solid #bfdbfe;
            display: flex;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
            position: relative;
            z-index: 10000; /* Above loading overlay */
        }
        
        .refresh-btn {
            padding: 0.5rem 1rem;
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            font-size: 0.875rem;
            transition: all 0.2s;
        }
        
        .refresh-btn:hover {
            background: #2563eb;
            transform: translateY(-1px);
        }
        
        /* Highlighted Load Index File button */
        #load-index-btn {
            background: #10b981 !important;
            font-size: 1rem !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
        }
        
        #load-index-btn:hover {
            background: #059669 !important;
            box-shadow: 0 6px 16px rgba(16, 185, 129, 0.6);
        }
        
        .refresh-instructions {
            color: #475569;
            font-size: 0.875rem;
            flex: 1;
        }
        
        .refresh-instructions code {
            background: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.8125rem;
        }
        
        /* Empty state with error styling */
        .empty-state-error {
            padding: 3rem;
            text-align: center;
            background: #fef2f2;
            border: 2px solid #fecaca;
            border-radius: 8px;
            margin: 2rem 0;
        }
        
        .empty-state-error h2 {
            color: #dc2626;
            margin-bottom: 1rem;
        }
        
        .empty-state-error ol {
            text-align: left;
            display: inline-block;
            color: #666;
            margin: 1rem 0;
        }
        
        .empty-state-error .fix-instructions {
            background: #eff6ff;
            padding: 1rem;
            border-radius: 8px;
            border: 2px solid #bfdbfe;
            margin-top: 1rem;
        }
        
        .empty-state-error .fix-instructions pre {
            margin-top: 0.5rem;
            text-align: left;
            background: white;
            padding: 0.75rem;
            border-radius: 4px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <!-- Loading Overlay -->
    <div class="loading-overlay" id="loading-overlay">
        <div style="text-align: center;">
            <div class="loading-spinner"></div>
            <p style="color: #666; font-size: 1rem;">Loading artifacts...</p>
        </div>
    </div>
    
    <div class="header">
        <h1>📚 Agent Orchestrator - Artifact Review Console</h1>
        <div class="subtitle">
            Review, approve, and prepare artifacts for LLM handoff
            <span id="generated-time" style="opacity: 0.8; font-size: 0.85em; margin-left: 1rem; display: none;">
                Last scanned: <span id="scan-timestamp">—</span>
            </span>
        </div>
        <span class="server-status disconnected" id="server-status">
            <span class="dot"></span>
            <span id="server-status-text">Server: Checking...</span>
        </span>
    </div>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-number" id="total-count">0</div>
            <div class="stat-label">Total Artifacts</div>
        </div>
        <div class="stat">
            <div class="stat-number" id="intelligence-count">0</div>
            <div class="stat-label">Intelligence</div>
        </div>
        <div class="stat">
            <div class="stat-number" id="drafting-count">0</div>
            <div class="stat-label">Drafting</div>
        </div>
        <div class="stat">
            <div class="stat-number" id="execution-count">0</div>
            <div class="stat-label">Execution</div>
        </div>
        <div class="stat">
            <div class="stat-number" id="learning-count">0</div>
            <div class="stat-label">Learning</div>
        </div>
    </div>
    
    <!-- Refresh Controls -->
    <div class="refresh-controls" id="refresh-controls">
        <button class="refresh-btn" onclick="location.reload()" title="Reload current dashboard data">
            🔄 Refresh Dashboard
        </button>
        <input type="file" id="load-index" accept=".json" style="display: none;" onchange="loadIndexFile(event)">
        <button class="refresh-btn" id="load-index-btn" onclick="document.getElementById('load-index').click()" style="background: #10b981; font-size: 1rem; padding: 0.75rem 1.5rem; font-weight: 600;" title="Load ARTIFACT_INDEX.json file">
            📂 Load Index File
        </button>
        <div class="refresh-instructions">
            <strong>Need latest artifacts?</strong> Run: <code>python scripts/temporal__generate_artifact_index.py</code>
        </div>
    </div>
    
    <div class="container">
        <!-- Review Progress Bar -->
        <div class="review-progress">
            <h3 style="margin: 0 0 0.75rem 0; color: #1e40af;">📊 Review Progress</h3>
            <div class="progress-bar-container">
                <div class="progress-bar" id="progress-bar" style="width: 0%">0%</div>
            </div>
            <div class="progress-stats">
                <div class="progress-stat reviewed">
                    <div class="dot"></div>
                    <span>Reviewed: <strong id="reviewed-count">0</strong></span>
                </div>
                <div class="progress-stat pending">
                    <div class="dot"></div>
                    <span>Unreviewed: <strong id="unreviewed-count-progress">0</strong></span>
                </div>
                <div class="progress-stat approved">
                    <div class="dot"></div>
                    <span>LLM Ready: <strong id="llm-ready-progress">0</strong></span>
                </div>
            </div>
        </div>
        
        <!-- Batch Actions Panel -->
        <div class="batch-actions" id="batch-actions">
            <div class="batch-actions-header">
                <div class="batch-select-all">
                    <input type="checkbox" id="select-all-checkbox" onchange="toggleSelectAll()">
                    <label for="select-all-checkbox"><strong>Select All</strong></label>
                    <span id="selected-count" style="margin-left: 0.5rem; color: #475569;">0 selected</span>
                </div>
                <button onclick="exitBatchMode()" style="padding: 0.25rem 0.75rem; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer;">Exit Batch Mode</button>
            </div>
            <div class="batch-actions-buttons">
                <button class="review-btn approve" onclick="batchApprove()">✓ Approve Selected</button>
                <button class="review-btn revise" onclick="batchRevise()">↻ Revise Selected</button>
                <button class="review-btn reject" onclick="batchReject()">✗ Reject Selected</button>
            </div>
        </div>
        
        <!-- Brief Generation Panel -->
        <div class="brief-panel">
            <h3>📋 One-Look Brief Generator</h3>
            <p style="margin-bottom: 1rem; color: #475569;">
                Generate a comprehensive briefing document for all approved artifacts selected for LLM handoff.
                The brief answers: What, Why, Who, How, and What Exactly is Being Sent.
            </p>
            <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                <button class="brief-btn" onclick="generateBrief()" id="generate-brief-btn">
                    Generate One-Look Brief
                </button>
                <span id="llm-ready-count" style="color: #475569;">0 artifacts ready for LLM</span>
                <a href="/api/brief/md" target="_blank" id="view-brief-link" style="display: none; color: #3b82f6;">View Latest Brief</a>
            </div>
        </div>
        
        <!-- Review Status Filters -->
        <div class="filter-bar" id="filter-bar">
            <button class="filter-btn active" data-filter="all">
                All <span class="count" id="filter-all-count">0</span>
            </button>
            <button class="filter-btn" data-filter="unreviewed">
                Unreviewed <span class="count" id="filter-unreviewed-count">0</span>
            </button>
            <button class="filter-btn" data-filter="APPROVE">
                Approved <span class="count" id="filter-approve-count">0</span>
            </button>
            <button class="filter-btn" data-filter="REVISE">
                Needs Revision <span class="count" id="filter-revise-count">0</span>
            </button>
            <button class="filter-btn" data-filter="REJECT">
                Rejected <span class="count" id="filter-reject-count">0</span>
            </button>
            <button class="filter-btn" data-filter="llm-ready">
                LLM Ready <span class="count" id="filter-llm-count">0</span>
            </button>
        </div>
        
        <input type="text" class="search-box" id="search" placeholder="🔍 Search artifacts by name, path, or type...">
        
        <div class="tabs">
            <div class="tab active" data-tab="all">All Artifacts</div>
            <div class="tab" data-tab="intelligence">🔍 Intelligence</div>
            <div class="tab" data-tab="drafting">✍️ Drafting</div>
            <div class="tab" data-tab="execution">⚙️ Execution</div>
            <div class="tab" data-tab="learning">📐 Learning</div>
            <div class="tab" data-tab="policy">📋 Policy</div>
            <div class="tab" data-tab="system">🔧 System</div>
        </div>
        
        <div id="tab-contents"></div>
    </div>
    
    <!-- Keyboard Shortcuts Hint -->
    <div class="shortcuts-hint" id="shortcuts-hint">
        <div style="font-weight: 600; margin-bottom: 0.5rem;">Keyboard Shortcuts:</div>
        <div><kbd>Ctrl+B</kbd> - Batch mode</div>
        <div><kbd>N</kbd> - Next unreviewed artifact</div>
        <div><kbd>?</kbd> - Show/hide this hint</div>
    </div>
    
    <script>
        // Artifacts data - loaded asynchronously from JSON file
        let artifactsData = {};
        let artifactsLoaded = false;
        
        // Review state
        let reviewStatuses = {};  // { artifactPath: { decision, reason, selected_for_llm, intended_recipient, why_sending } }
        let serverConnected = false;
        let currentReviewFilter = 'all';
        const API_BASE = 'http://localhost:8080';
        
        // Load artifacts data from JSON file
        async function loadArtifactsData() {
            const loadingOverlay = document.getElementById('loading-overlay');
            const statusText = loadingOverlay?.querySelector('p');
            
            try {
                // Try to load from ARTIFACT_INDEX.json in same directory
                const jsonUrl = 'ARTIFACT_INDEX.json';
                const response = await fetch(jsonUrl);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const indexData = await response.json();
                
                // Extract artifacts from the JSON structure
                if (indexData.artifacts) {
                    artifactsData = indexData.artifacts;
                } else if (indexData.intelligence || indexData.drafting) {
                    // Direct artifacts structure
                    artifactsData = indexData;
                } else {
                    throw new Error('Invalid JSON structure: missing artifacts property');
                }
                
                artifactsLoaded = true;
                
                // Update timestamp if available
                if (indexData._meta && indexData._meta.generated_at) {
                    const timestampEl = document.getElementById('scan-timestamp');
                    if (timestampEl) {
                        const date = new Date(indexData._meta.generated_at);
                        timestampEl.textContent = date.toLocaleString();
                        document.getElementById('generated-time').style.display = 'inline';
                    }
                }
                
                // Update status message
                if (statusText) {
                    statusText.textContent = `✅ Loaded ${Object.values(artifactsData).flat().length} artifacts`;
                }
                
                console.log('✅ Artifacts loaded successfully:', {
                    categories: Object.keys(artifactsData),
                    total: Object.values(artifactsData).flat().length
                });
                
                return true;
                
            } catch (error) {
                console.warn('Could not load ARTIFACT_INDEX.json via fetch:', error);
                
                // Update overlay to show file picker button directly in overlay
                if (loadingOverlay && statusText) {
                    loadingOverlay.innerHTML = `
                        <div style="text-align: center; max-width: 600px; padding: 2rem;">
                            <div style="font-size: 3rem; margin-bottom: 1rem;">📂</div>
                            <h2 style="color: #1e40af; margin-bottom: 1rem; font-size: 1.5rem;">Load Artifact Index File</h2>
                            <p style="color: #666; margin-bottom: 1.5rem; font-size: 1rem;">
                                Could not automatically load ARTIFACT_INDEX.json<br>
                                <small style="font-size: 0.875em;">This is normal when opening via file:// protocol</small>
                            </p>
                            <input type="file" id="load-index-overlay" accept=".json" style="display: none;" onchange="loadIndexFile(event)">
                            <button onclick="document.getElementById('load-index-overlay').click()" style="background: #10b981; color: white; border: none; padding: 1rem 2rem; border-radius: 8px; font-size: 1.125rem; font-weight: 600; cursor: pointer; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4); transition: all 0.2s; animation: pulse 2s infinite;" onmouseover="this.style.background='#059669'; this.style.transform='scale(1.05)'" onmouseout="this.style.background='#10b981'; this.style.transform='scale(1)'">
                                📂 Select ARTIFACT_INDEX.json File
                            </button>
                            <p style="color: #666; margin-top: 1.5rem; font-size: 0.875rem;">
                                The file should be in the same directory as this HTML file<br>
                                <code style="background: #f3f4f6; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8125rem;">agent-orchestrator/artifacts/ARTIFACT_INDEX.json</code>
                            </p>
                        </div>
                    `;
                    
                    // Add pulsing animation
                    const style = document.createElement('style');
                    style.textContent = `
                        @keyframes pulse {
                            0%, 100% { transform: scale(1); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4); }
                            50% { transform: scale(1.03); box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6); }
                        }
                    `;
                    document.head.appendChild(style);
                }
                
                return false;
            }
        }
        
        // Check server connection
        async function checkServerConnection() {
            const statusEl = document.getElementById('server-status');
            const statusText = document.getElementById('server-status-text');
            try {
                const response = await fetch(API_BASE + '/api/health');
                if (response.ok) {
                    serverConnected = true;
                    statusEl.classList.remove('disconnected');
                    statusEl.classList.add('connected');
                    statusText.textContent = 'Server: Connected';
                    await loadReviewStatuses();
                } else {
                    throw new Error('Server not healthy');
                }
            } catch (e) {
                serverConnected = false;
                statusEl.classList.remove('connected');
                statusEl.classList.add('disconnected');
                statusText.textContent = 'Server: Not Running';
            }
        }
        
        // Load existing review statuses from server
        async function loadReviewStatuses() {
            if (!serverConnected) return;
            try {
                const response = await fetch(API_BASE + '/api/reviews');
                const data = await response.json();
                
                // Build status map from reviews (latest review per artifact)
                reviewStatuses = {};
                for (const review of (data.reviews || [])) {
                    const existing = reviewStatuses[review.artifact_path];
                    if (!existing || review.reviewed_at > existing.reviewed_at) {
                        reviewStatuses[review.artifact_path] = {
                            decision: review.decision,
                            reason: review.reason,
                            selected_for_llm: review.selected_for_llm,
                            intended_recipient: review.intended_recipient,
                            why_sending: review.why_sending,
                            reviewed_at: review.reviewed_at
                        };
                    }
                }
                
                updateFilterCounts();
                updateDisplay();
            } catch (e) {
                console.error('Failed to load reviews:', e);
            }
        }
        
        // Update filter counts and progress
        function updateFilterCounts() {
            if (!artifactsLoaded || !artifactsData || Object.keys(artifactsData).length === 0) {
                // Data not loaded yet, set all counts to 0
                document.getElementById('filter-all-count').textContent = '0';
                document.getElementById('filter-unreviewed-count').textContent = '0';
                document.getElementById('filter-approve-count').textContent = '0';
                document.getElementById('filter-revise-count').textContent = '0';
                document.getElementById('filter-reject-count').textContent = '0';
                document.getElementById('filter-llm-count').textContent = '0';
                document.getElementById('llm-ready-count').textContent = '0 artifacts ready for LLM';
                document.getElementById('reviewed-count').textContent = '0';
                document.getElementById('unreviewed-count-progress').textContent = '0';
                document.getElementById('llm-ready-progress').textContent = '0';
                const progressBar = document.getElementById('progress-bar');
                if (progressBar) {
                    progressBar.style.width = '0%';
                    progressBar.textContent = '0%';
                }
                return;
            }
            
            const allArtifacts = Object.values(artifactsData).flat();
            const total = allArtifacts.length;
            
            let approved = 0, rejected = 0, revise = 0, llmReady = 0;
            for (const artifact of allArtifacts) {
                const path = artifact.path.replace(/\\\\/g, '/');
                const status = reviewStatuses[path];
                if (status) {
                    if (status.decision === 'APPROVE') approved++;
                    if (status.decision === 'REJECT') rejected++;
                    if (status.decision === 'REVISE') revise++;
                    if (status.decision === 'APPROVE' && status.selected_for_llm) llmReady++;
                }
            }
            
            const unreviewed = total - approved - rejected - revise;
            const reviewed = total - unreviewed;
            const progressPercent = total > 0 ? Math.round((reviewed / total) * 100) : 0;
            
            // Update filter counts
            document.getElementById('filter-all-count').textContent = total;
            document.getElementById('filter-unreviewed-count').textContent = unreviewed;
            document.getElementById('filter-approve-count').textContent = approved;
            document.getElementById('filter-revise-count').textContent = revise;
            document.getElementById('filter-reject-count').textContent = rejected;
            document.getElementById('filter-llm-count').textContent = llmReady;
            document.getElementById('llm-ready-count').textContent = llmReady + ' artifacts ready for LLM';
            
            // Update progress bar
            const progressBar = document.getElementById('progress-bar');
            if (progressBar) {
                progressBar.style.width = progressPercent + '%';
                progressBar.textContent = progressPercent + '%';
            }
            
            // Update progress stats
            document.getElementById('reviewed-count').textContent = reviewed;
            document.getElementById('unreviewed-count-progress').textContent = unreviewed;
            document.getElementById('llm-ready-progress').textContent = llmReady;
            
            // Show/hide brief link
            const briefLink = document.getElementById('view-brief-link');
            if (llmReady > 0) {
                briefLink.style.display = 'inline';
            } else {
                briefLink.style.display = 'none';
            }
        }
        
        // Batch actions
        let batchMode = false;
        const selectedCards = new Set();
        
        function enterBatchMode() {
            batchMode = true;
            document.getElementById('batch-actions').classList.add('active');
            document.querySelectorAll('.artifact-card').forEach(card => {
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.className = 'review-checkbox';
                checkbox.onchange = () => {
                    if (checkbox.checked) {
                        selectedCards.add(card.id);
                    } else {
                        selectedCards.delete(card.id);
                    }
                    updateSelectedCount();
                };
                card.appendChild(checkbox);
            });
        }
        
        function exitBatchMode() {
            batchMode = false;
            document.getElementById('batch-actions').classList.remove('active');
            document.getElementById('select-all-checkbox').checked = false;
            document.querySelectorAll('.review-checkbox').forEach(cb => cb.style.display = 'none');
            selectedCards.clear();
            updateSelectedCount();
        }
        
        function toggleSelectAll() {
            const selectAll = document.getElementById('select-all-checkbox').checked;
            document.querySelectorAll('.review-checkbox').forEach(cb => {
                cb.checked = selectAll;
                const cardId = cb.parentElement.id;
                if (selectAll) {
                    selectedCards.add(cardId);
                } else {
                    selectedCards.delete(cardId);
                }
            });
            updateSelectedCount();
        }
        
        function updateSelectedCount() {
            document.getElementById('selected-count').textContent = selectedCards.size + ' selected';
        }
        
        async function batchApprove() {
            if (selectedCards.size === 0) {
                alert('No artifacts selected');
                return;
            }
            const reason = prompt('Reason for approving all selected artifacts:');
            if (!reason) return;
            
            for (const cardId of selectedCards) {
                const card = document.getElementById(cardId);
                const path = card.dataset.path;
                await submitBatchReview(path, 'APPROVE', reason);
            }
            exitBatchMode();
            updateDisplay();
        }
        
        async function batchRevise() {
            if (selectedCards.size === 0) {
                alert('No artifacts selected');
                return;
            }
            const reason = prompt('Reason for revising all selected artifacts:');
            if (!reason) return;
            
            for (const cardId of selectedCards) {
                const card = document.getElementById(cardId);
                const path = card.dataset.path;
                await submitBatchReview(path, 'REVISE', reason);
            }
            exitBatchMode();
            updateDisplay();
        }
        
        async function batchReject() {
            if (selectedCards.size === 0) {
                alert('No artifacts selected');
                return;
            }
            const reason = prompt('Reason for rejecting all selected artifacts:');
            if (!reason) return;
            
            for (const cardId of selectedCards) {
                const card = document.getElementById(cardId);
                const path = card.dataset.path;
                await submitBatchReview(path, 'REJECT', reason);
            }
            exitBatchMode();
            updateDisplay();
        }
        
        async function submitBatchReview(artifactPath, decision, reason) {
            if (!serverConnected) {
                console.warn('Server not connected, review not saved');
                // Still update local state
                reviewStatuses[artifactPath] = {
                    decision: decision,
                    reason: reason,
                    reviewed_at: new Date().toISOString()
                };
                return;
            }
            try {
                const response = await fetch(API_BASE + '/api/reviews', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        artifact_path: artifactPath,
                        decision: decision,
                        reason: reason,
                        selected_for_llm: false,
                        intended_recipient: '',
                        why_sending: ''
                    })
                });
                
                if (!response.ok) {
                    throw new Error('Failed to save review');
                }
                
                reviewStatuses[artifactPath] = {
                    decision: decision,
                    reason: reason,
                    reviewed_at: new Date().toISOString()
                };
            } catch (e) {
                console.error('Failed to submit batch review:', e);
                // Still update local state for UI
                reviewStatuses[artifactPath] = {
                    decision: decision,
                    reason: reason,
                    reviewed_at: new Date().toISOString()
                };
            }
        }
        
        // Navigate to next unreviewed artifact
        function goToNextUnreviewed() {
            const unreviewedCards = Array.from(document.querySelectorAll('[data-review-status="UNREVIEWED"]'));
            if (unreviewedCards.length === 0) {
                alert('All artifacts reviewed!');
                return;
            }
            
            // Find first visible unreviewed card or scroll to first
            const visibleCard = unreviewedCards.find(card => {
                const rect = card.getBoundingClientRect();
                return rect.top >= 0 && rect.bottom <= window.innerHeight;
            });
            
            const targetCard = visibleCard || unreviewedCards[0];
            const cardId = targetCard.id;
            
            toggleExpand(cardId);
            targetCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Focus on reason textarea
            setTimeout(() => {
                const reasonTextarea = document.getElementById('reason-' + cardId);
                if (reasonTextarea) reasonTextarea.focus();
            }, 500);
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + B: Batch mode
            if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
                e.preventDefault();
                if (batchMode) {
                    exitBatchMode();
                } else {
                    enterBatchMode();
                }
            }
            
            // N: Next unreviewed
            if (e.key === 'n' && !e.ctrlKey && !e.metaKey && document.activeElement.tagName !== 'TEXTAREA' && document.activeElement.tagName !== 'INPUT') {
                e.preventDefault();
                goToNextUnreviewed();
            }
            
            // Show shortcuts hint on ?
            if (e.key === '?' && !e.ctrlKey && !e.metaKey) {
                e.preventDefault();
                const hint = document.getElementById('shortcuts-hint');
                if (hint) {
                    hint.classList.toggle('active');
                    setTimeout(() => hint.classList.remove('active'), 5000);
                }
            }
        });
        
        // Set review decision (before submit)
        let pendingDecisions = {};  // { cardId: decision }
        function setReviewDecision(cardId, decision) {
            pendingDecisions[cardId] = decision;
            
            // Update button styles
            const buttons = document.querySelectorAll(`#review-${cardId} .review-btn`);
            buttons.forEach(btn => {
                btn.style.opacity = '0.5';
                btn.style.transform = 'scale(0.95)';
            });
            
            const activeBtn = document.querySelector(`#review-${cardId} .review-btn.${decision.toLowerCase()}`);
            if (activeBtn) {
                activeBtn.style.opacity = '1';
                activeBtn.style.transform = 'scale(1.05)';
            }
        }
        
        // Submit review to server
        async function submitReview(cardId, artifactPath) {
            if (!serverConnected) {
                alert('Review server not running!\\n\\nStart the server with:\\nartifacts/START_REVIEW_SERVER.bat');
                return;
            }
            
            const decision = pendingDecisions[cardId];
            if (!decision) {
                alert('Please select a decision (Approve, Revise, or Reject) first.');
                return;
            }
            
            const reason = document.getElementById('reason-' + cardId).value.trim();
            if (!reason) {
                alert('Please provide a reason for your decision.');
                return;
            }
            
            const selectedForLlm = document.getElementById('llm-' + cardId).checked;
            const recipient = document.getElementById('recipient-' + cardId).value;
            const whySending = document.getElementById('why-sending-' + cardId).value.trim();
            
            if (selectedForLlm && !recipient) {
                alert('Please select a recipient if including in LLM packet.');
                return;
            }
            
            try {
                const response = await fetch(API_BASE + '/api/reviews', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        artifact_path: artifactPath,
                        decision: decision,
                        reason: reason,
                        selected_for_llm: selectedForLlm,
                        intended_recipient: recipient,
                        why_sending: whySending
                    })
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to submit review');
                }
                
                const result = await response.json();
                
                // Update local state
                reviewStatuses[artifactPath] = {
                    decision: decision,
                    reason: reason,
                    selected_for_llm: selectedForLlm,
                    intended_recipient: recipient,
                    why_sending: whySending,
                    reviewed_at: new Date().toISOString()
                };
                
                // Clear pending decision
                delete pendingDecisions[cardId];
                
                // Update UI
                updateFilterCounts();
                
                // Update card badge
                const card = document.getElementById(cardId);
                const badge = card.querySelector('.review-status-badge');
                badge.className = 'review-status-badge ' + decision;
                badge.textContent = decision;
                card.dataset.reviewStatus = decision;
                
                // Flash success
                card.style.borderColor = '#22c55e';
                setTimeout(() => {
                    card.style.borderColor = '';
                }, 1000);
                
                alert('Review submitted: ' + decision);
                
            } catch (e) {
                alert('Error submitting review: ' + e.message);
            }
        }
        
        // Generate one-look brief
        async function generateBrief() {
            if (!serverConnected) {
                alert('Review server not running!\\n\\nStart the server with:\\nartifacts/START_REVIEW_SERVER.bat');
                return;
            }
            
            const btn = document.getElementById('generate-brief-btn');
            btn.disabled = true;
            btn.textContent = 'Generating...';
            
            try {
                const response = await fetch(API_BASE + '/api/brief', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        title: 'Artifact Review Brief - ' + new Date().toLocaleDateString(),
                        description: 'Comprehensive briefing for LLM handoff',
                        include_content_excerpts: true,
                        max_excerpt_length: 500
                    })
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to generate brief');
                }
                
                const result = await response.json();
                
                alert('Brief generated!\\n\\n' + result.artifact_count + ' artifacts included.\\n\\nOpening brief...');
                
                // Open the brief
                window.open(API_BASE + '/api/brief/md', '_blank');
                
                // Show link
                document.getElementById('view-brief-link').style.display = 'inline';
                
            } catch (e) {
                alert('Error generating brief: ' + e.message);
            } finally {
                btn.disabled = false;
                btn.textContent = 'Generate One-Look Brief';
            }
        }
        
        // Update stats display (consolidated function)
        function updateStats() {
            // Guard against empty or unloaded data
            if (!artifactsLoaded || !artifactsData || Object.keys(artifactsData).length === 0) {
                const totalEl = document.getElementById('total-count');
                const intelEl = document.getElementById('intelligence-count');
                const draftEl = document.getElementById('drafting-count');
                const execEl = document.getElementById('execution-count');
                const learnEl = document.getElementById('learning-count');
                
                if (totalEl) totalEl.textContent = '0';
                if (intelEl) intelEl.textContent = '0';
                if (draftEl) draftEl.textContent = '0';
                if (execEl) execEl.textContent = '0';
                if (learnEl) learnEl.textContent = '0';
                
                updateFilterCounts();
                updateDisplay();
                return;
            }
            
            let total = 0;
            for (const category in artifactsData) {
                if (Array.isArray(artifactsData[category])) {
                    total += artifactsData[category].length;
                }
            }
            
            const totalEl = document.getElementById('total-count');
            const intelEl = document.getElementById('intelligence-count');
            const draftEl = document.getElementById('drafting-count');
            const execEl = document.getElementById('execution-count');
            const learnEl = document.getElementById('learning-count');
            
            if (totalEl) totalEl.textContent = total;
            if (intelEl) intelEl.textContent = (artifactsData.intelligence && Array.isArray(artifactsData.intelligence)) ? artifactsData.intelligence.length : 0;
            if (draftEl) draftEl.textContent = (artifactsData.drafting && Array.isArray(artifactsData.drafting)) ? artifactsData.drafting.length : 0;
            if (execEl) execEl.textContent = (artifactsData.execution && Array.isArray(artifactsData.execution)) ? artifactsData.execution.length : 0;
            if (learnEl) learnEl.textContent = (artifactsData.learning && Array.isArray(artifactsData.learning)) ? artifactsData.learning.length : 0;
            
            updateFilterCounts();
            updateDisplay();
        }
        
        // Initialize stats (alias for updateStats)
        function initializeStats() {
            updateStats();
        }
        
        // Validate artifacts data
        function validateData() {
            const allArtifacts = Object.values(artifactsData || {}).flat();
            if (allArtifacts.length === 0) {
                const container = document.getElementById('tab-contents');
                if (container) {
                    container.innerHTML = `
                        <div class="empty-state-error">
                            <h2>⚠️ No Artifacts Found</h2>
                            <p style="color: #666; margin-bottom: 1.5rem;">
                                The dashboard has no artifact data. This usually means:
                            </p>
                            <ol>
                                <li>The JSON file (ARTIFACT_INDEX.json) has not been loaded yet</li>
                                <li>The artifacts directory has no JSON files</li>
                                <li>The generation script encountered errors</li>
                            </ol>
                            <div class="fix-instructions">
                                <strong style="color: #1e40af;">To fix this:</strong>
                                <pre><code>cd agent-orchestrator
python scripts/temporal__generate_artifact_index.py

Then click "📂 Load Index File" button to load ARTIFACT_INDEX.json</code></pre>
                            </div>
                        </div>
                    `;
                }
                return false;
            }
            return true;
        }
        
        // Load index file from file picker (updated to set artifactsLoaded)
        function loadIndexFile(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            const loadingOverlay = document.getElementById('loading-overlay');
            
            // Update overlay to show loading state
            if (loadingOverlay) {
                loadingOverlay.innerHTML = `
                    <div style="text-align: center;">
                        <div class="loading-spinner"></div>
                        <p style="color: #666; font-size: 1rem; margin-top: 1rem;">Loading ${file.name}...</p>
                    </div>
                `;
            }
            
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const indexData = JSON.parse(e.target.result);
                    
                    // Extract artifacts from the JSON structure
                    if (indexData.artifacts) {
                        artifactsData = indexData.artifacts;
                    } else if (indexData.intelligence || indexData.drafting) {
                        // Direct artifacts structure
                        artifactsData = indexData;
                    } else {
                        throw new Error('Invalid JSON structure: missing artifacts property');
                    }
                    
                    artifactsLoaded = true;
                    
                    // Update timestamp if available
                    if (indexData._meta && indexData._meta.generated_at) {
                        const timestampEl = document.getElementById('scan-timestamp');
                        if (timestampEl) {
                            const date = new Date(indexData._meta.generated_at);
                            timestampEl.textContent = date.toLocaleString();
                            document.getElementById('generated-time').style.display = 'inline';
                        }
                    }
                    
                    // Validate and initialize
                    if (!validateData()) {
                        if (loadingOverlay) {
                            loadingOverlay.innerHTML = `
                                <div style="text-align: center; padding: 2rem;">
                                    <div style="font-size: 3rem; margin-bottom: 1rem;">❌</div>
                                    <h2 style="color: #dc2626; margin-bottom: 1rem;">Invalid Data</h2>
                                    <p style="color: #666;">The JSON file does not contain valid artifact data.</p>
                                    <button onclick="location.reload()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer;">Reload Page</button>
                                </div>
                            `;
                        }
                        return;
                    }
                    
                    // Update UI
                    updateStats();
                    updateDisplay();
                    
                    // Hide loading overlay with success message
                    if (loadingOverlay) {
                        const totalArtifacts = Object.values(artifactsData).flat().length;
                        loadingOverlay.innerHTML = `
                            <div style="text-align: center; padding: 2rem;">
                                <div style="font-size: 3rem; margin-bottom: 1rem;">✅</div>
                                <h2 style="color: #10b981; margin-bottom: 1rem;">Loaded ${totalArtifacts} Artifacts!</h2>
                                <p style="color: #666;">Dashboard is ready</p>
                            </div>
                        `;
                        setTimeout(() => {
                            loadingOverlay.style.opacity = '0';
                            setTimeout(() => {
                                loadingOverlay.style.display = 'none';
                            }, 300);
                        }, 1500);
                    }
                    
                    console.log('✅ Loaded artifacts from file:', Object.values(artifactsData).flat().length);
                    
                } catch (error) {
                    artifactsLoaded = false;
                    if (loadingOverlay) {
                        loadingOverlay.innerHTML = `
                            <div style="text-align: center; padding: 2rem;">
                                <div style="font-size: 3rem; margin-bottom: 1rem;">❌</div>
                                <h2 style="color: #dc2626; margin-bottom: 1rem;">Error Loading File</h2>
                                <p style="color: #666; margin-bottom: 1rem;">${error.message}</p>
                                <input type="file" id="load-index-retry" accept=".json" style="display: none;" onchange="loadIndexFile(event)">
                                <button onclick="document.getElementById('load-index-retry').click()" style="padding: 0.5rem 1rem; background: #10b981; color: white; border: none; border-radius: 6px; cursor: pointer; margin-right: 0.5rem;">Try Again</button>
                                <button onclick="location.reload()" style="padding: 0.5rem 1rem; background: #6b7280; color: white; border: none; border-radius: 6px; cursor: pointer;">Reload Page</button>
                            </div>
                        `;
                    }
                    alert('❌ Error loading index file: ' + error.message + '\\n\\nMake sure you selected ARTIFACT_INDEX.json');
                }
            };
            reader.onerror = function() {
                artifactsLoaded = false;
                if (statusText) statusText.textContent = '❌ Error reading file';
                alert('❌ Error reading file');
            };
            reader.readAsText(file);
        }
        
        // Initialize when DOM is ready
        async function initializePage() {
            console.log('=== Initializing Artifact Viewer ===');
            
            const loadingOverlay = document.getElementById('loading-overlay');
            const statusText = loadingOverlay?.querySelector('p');
            
            // Show loading overlay
            if (loadingOverlay) {
                loadingOverlay.style.display = 'flex';
            }
            
            // Try to load artifacts data from JSON file
            const loaded = await loadArtifactsData();
            
            if (!loaded) {
                // Fetch failed (likely file:// protocol)
                // Note: loadArtifactsData() already handles hiding overlay and highlighting button
                console.log('Auto-load failed, waiting for manual file selection...');
                // The loadArtifactsData function already hides overlay and highlights the button
                // So we just return here - user will see the highlighted "Load Index File" button
                return;
            }
            
            // Data loaded successfully, validate and initialize
            if (!artifactsLoaded || !validateData()) {
                if (loadingOverlay) loadingOverlay.style.display = 'none';
                return;
            }
            
            // Wait a tiny bit to ensure DOM elements exist
            setTimeout(() => {
                // Calculate initial stats
                updateStats();
                
                // Hide loading overlay
                if (loadingOverlay) {
                    loadingOverlay.style.transition = 'opacity 0.3s';
                    loadingOverlay.style.opacity = '0';
                    setTimeout(() => {
                        loadingOverlay.style.display = 'none';
                    }, 300);
                }
                
                // Try to load from API (will update stats if successful)
                checkServerConnection();
                
                // Auto-expand first unreviewed artifact for immediate action
                setTimeout(() => {
                    const unreviewedCards = document.querySelectorAll('[data-review-status="UNREVIEWED"]');
                    if (unreviewedCards.length > 0) {
                        const firstCard = unreviewedCards[0];
                        const cardId = firstCard.id;
                        toggleExpand(cardId);
                        // Scroll into view
                        firstCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }, 500);
            }, 100);
        }
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initializePage);
        } else {
            initializePage();
        }
        
        // Periodically check server connection
        setInterval(checkServerConnection, 30000);
        
        let currentTab = 'all';
        let currentFilter = '';
        
        function renderArtifacts(category, filter = '') {
            // Check if data is completely empty (not loaded yet)
            const allArtifacts = Object.values(artifactsData || {}).flat();
            if (allArtifacts.length === 0 || !artifactsLoaded) {
                return `
                    <div class="empty-state-error">
                        <h2>⚠️ No Artifacts Loaded</h2>
                        <p style="color: #666; margin-bottom: 1.5rem;">
                            Artifact data has not been loaded yet. Please:
                        </p>
                        <ol>
                            <li>Click the "📂 Load Index File" button above</li>
                            <li>Select the ARTIFACT_INDEX.json file</li>
                            <li>Or regenerate the dashboard: <code>python scripts/temporal__generate_artifact_index.py</code></li>
                        </ol>
                        <div class="fix-instructions">
                            <strong style="color: #1e40af;">The JSON file should be in the same directory as this HTML file.</strong>
                        </div>
                    </div>
                `;
            }
            
            let artifacts = [];
            if (category === 'all') {
                artifacts = Object.values(artifactsData).flat();
            } else {
                artifacts = artifactsData[category] || [];
            }
            
            // Apply text filter
            if (filter) {
                const lowerFilter = filter.toLowerCase();
                artifacts = artifacts.filter(a => 
                    a.name.toLowerCase().includes(lowerFilter) ||
                    a.path.toLowerCase().includes(lowerFilter) ||
                    (a.artifact_type && a.artifact_type.toLowerCase().includes(lowerFilter)) ||
                    (a.meta && JSON.stringify(a.meta).toLowerCase().includes(lowerFilter))
                );
            }
            
            // Apply review status filter
            if (currentReviewFilter && currentReviewFilter !== 'all') {
                artifacts = artifacts.filter(a => {
                    const path = a.path.replace(/\\\\/g, '/');
                    const status = reviewStatuses[path];
                    
                    if (currentReviewFilter === 'unreviewed') {
                        return !status || status.decision === 'UNREVIEWED';
                    } else if (currentReviewFilter === 'llm-ready') {
                        return status && status.decision === 'APPROVE' && status.selected_for_llm;
                    } else {
                        return status && status.decision === currentReviewFilter;
                    }
                });
            }
            
            if (artifacts.length === 0) {
                return '<div class="empty-state">No artifacts found matching filters. Try adjusting your search or filter criteria.</div>';
            }
            
            return artifacts.map(artifact => {
                const status = artifact.meta?.status || 'UNKNOWN';
                const badgeClass = category === 'all' ? (artifact.directory.startsWith('intel_') ? 'intelligence' :
                                                         artifact.directory.startsWith('draft_') ? 'drafting' :
                                                         artifact.directory.startsWith('execution_') ? 'execution' :
                                                         artifact.directory.startsWith('learning_') ? 'learning' :
                                                         artifact.directory === 'policy' ? 'policy' : 'system') : category;
                
                const artifactPath = artifact.full_path.replace(/\\\\/g, '/');
                const relativePath = artifact.path.replace(/\\\\/g, '/');
                const artifactType = artifact.artifact_type || artifact.name.replace('.json', '');
                
                // Create unique card ID
                const cardId = 'card-' + btoa(artifact.path).replace(/[^a-zA-Z0-9]/g, '').substring(0, 20);
                
                // Generate preview content
                let previewContent = '<div class="preview-meta"><strong>Quick Preview</strong><br>';
                if (artifact.meta) {
                    if (artifact.meta.artifact_name) previewContent += `Name: ${artifact.meta.artifact_name.replace(/"/g, '&quot;')}<br>`;
                    if (artifact.meta.agent_id) previewContent += `Agent: <code>${artifact.meta.agent_id}</code><br>`;
                    if (artifact.meta.artifact_type) previewContent += `Type: <code>${artifact.meta.artifact_type}</code><br>`;
                    if (artifact.meta.status) previewContent += `Status: <span class="status ${artifact.meta.status}">${artifact.meta.status}</span><br>`;
                    if (artifact.meta.requires_review) previewContent += `Review Gate: <code>${artifact.meta.requires_review}</code><br>`;
                }
                previewContent += '</div>';
                previewContent += '<div class="preview-content">';
                previewContent += '<div class="preview-section"><div class="preview-section-title">Path:</div><code>' + artifact.path.replace(/"/g, '&quot;') + '</code></div>';
                previewContent += '<div class="preview-section"><em>Use "View Formatted" for full content</em></div>';
                previewContent += '</div>';
                
                // Get review status for this artifact
                const reviewStatus = reviewStatuses[relativePath] || { decision: 'UNREVIEWED', reason: '', selected_for_llm: false };
                
                return `
                    <div class="artifact-card" id="${cardId}" data-path="${relativePath}" data-review-status="${reviewStatus.decision}">
                        <span class="review-status-badge ${reviewStatus.decision}">${reviewStatus.decision}</span>
                        <h3>${artifact.name}</h3>
                        <div class="path" title="${artifact.full_path}">${artifact.path}</div>
                        <div class="meta">
                            <div class="meta-item"><strong>Directory:</strong> ${artifact.directory}</div>
                            <div class="meta-item"><strong>Type:</strong> ${artifact.artifact_type}</div>
                            <div class="meta-item"><strong>Size:</strong> ${(artifact.size / 1024).toFixed(1)} KB</div>
                            <div class="meta-item"><strong>Modified:</strong> ${new Date(artifact.modified).toLocaleString()}</div>
                            ${artifact.meta?.generated_at ? `<div class="meta-item"><strong>Generated:</strong> ${artifact.meta.generated_at}</div>` : ''}
                            ${status !== 'UNKNOWN' ? `<span class="status ${status}">${status}</span>` : ''}
                            <span class="badge ${badgeClass}">${badgeClass}</span>
                        </div>
                        <button class="expand-btn" onclick="toggleExpand('${cardId}')" id="btn-${cardId}">▼ Expand Preview</button>
                        <div class="artifact-preview" id="preview-${cardId}">
                            ${previewContent}
                        </div>
                        <div class="action-buttons">
                            <button class="open-file-btn" onclick="openArtifactFile('${artifactPath.replace(/'/g, "\\'")}')">📄 Open File</button>
                            <button class="action-btn" onclick="viewFormattedArtifact('${relativePath.replace(/'/g, "\\'")}', '${artifactType.replace(/'/g, "\\'")}')">📝 View Formatted</button>
                            <button class="action-btn codex" onclick="viewCodexReview('${relativePath.replace(/'/g, "\\'")}')">🔍 Codex Review</button>
                            <button class="action-btn debug" onclick="showDebugInfo('${relativePath.replace(/'/g, "\\'")}', '${JSON.stringify(artifact.meta || {}).replace(/'/g, "\\'")}')">🐛 Debug Info</button>
                        </div>
                        
                        <!-- Review Controls -->
                        <div class="review-controls ${reviewStatus.decision !== 'UNREVIEWED' ? 'has-status' : ''}" id="review-${cardId}">
                            <div class="review-buttons">
                                <button class="review-btn approve" onclick="setReviewDecision('${cardId}', 'APPROVE')">✓ Approve</button>
                                <button class="review-btn revise" onclick="setReviewDecision('${cardId}', 'REVISE')">↻ Revise</button>
                                <button class="review-btn reject" onclick="setReviewDecision('${cardId}', 'REJECT')">✗ Reject</button>
                            </div>
                            <textarea class="review-reason" id="reason-${cardId}" placeholder="Why this decision? (required)">${reviewStatus.reason || ''}</textarea>
                            <div class="review-options">
                                <label class="review-option">
                                    <input type="checkbox" id="llm-${cardId}" ${reviewStatus.selected_for_llm ? 'checked' : ''}>
                                    Include in LLM packet
                                </label>
                                <label class="review-option">
                                    Recipient:
                                    <select id="recipient-${cardId}">
                                        <option value="">Select...</option>
                                        <option value="ChatGPT" ${reviewStatus.intended_recipient === 'ChatGPT' ? 'selected' : ''}>ChatGPT</option>
                                        <option value="Claude" ${reviewStatus.intended_recipient === 'Claude' ? 'selected' : ''}>Claude</option>
                                        <option value="Codex" ${reviewStatus.intended_recipient === 'Codex' ? 'selected' : ''}>Codex</option>
                                        <option value="Internal" ${reviewStatus.intended_recipient === 'Internal' ? 'selected' : ''}>Internal</option>
                                    </select>
                                </label>
                            </div>
                            <input type="text" class="review-reason" id="why-sending-${cardId}" placeholder="Why sending to LLM? (if selected)" value="${reviewStatus.why_sending || ''}" style="min-height: auto;">
                            <button class="review-submit" onclick="submitReview('${cardId}', '${relativePath.replace(/'/g, "\\'")}')">Submit Review</button>
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        function updateDisplay() {
            const tabContents = document.getElementById('tab-contents');
            const html = `
                <div class="tab-content active">
                    <div class="artifact-grid">
                        ${renderArtifacts(currentTab, currentFilter)}
                    </div>
                </div>
            `;
            tabContents.innerHTML = html;
        }
        
        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                currentTab = tab.dataset.tab;
                updateDisplay();
            });
        });
        
        // Review filter switching
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentReviewFilter = btn.dataset.filter;
                updateDisplay();
            });
        });
        
        // Search
        document.getElementById('search').addEventListener('input', (e) => {
            currentFilter = e.target.value;
            updateDisplay();
        });
        
        // Initial render
        updateDisplay();
        
        // Expand/collapse functionality
        function toggleExpand(cardId) {
            const card = document.getElementById(cardId);
            const preview = document.getElementById('preview-' + cardId);
            const btn = document.getElementById('btn-' + cardId);
            
            if (card.classList.contains('expanded')) {
                card.classList.remove('expanded');
                btn.textContent = '▼ Expand Preview';
                btn.classList.remove('expanded');
            } else {
                card.classList.add('expanded');
                btn.textContent = '▲ Collapse Preview';
                btn.classList.add('expanded');
            }
        }
        
        // Generate artifact preview content (called during rendering)
        function generateArtifactPreview(artifact) {
            let preview = '<div class="preview-meta">';
            preview += '<strong>Quick Preview</strong><br>';
            if (artifact.meta) {
                if (artifact.meta.artifact_name) preview += `Name: ${escapeHtml(artifact.meta.artifact_name)}<br>`;
                if (artifact.meta.agent_id) preview += `Agent: <code>${escapeHtml(artifact.meta.agent_id)}</code><br>`;
                if (artifact.meta.artifact_type) preview += `Type: <code>${escapeHtml(artifact.meta.artifact_type)}</code><br>`;
                if (artifact.meta.status) preview += `Status: <span class="status ${artifact.meta.status}">${escapeHtml(artifact.meta.status)}</span><br>`;
                if (artifact.meta.requires_review) preview += `Review Gate: <code>${escapeHtml(artifact.meta.requires_review)}</code><br>`;
                if (artifact.meta.generated_at) preview += `Generated: ${escapeHtml(artifact.meta.generated_at)}<br>`;
            }
            preview += '</div>';
            
            preview += '<div class="preview-content">';
            preview += '<div class="preview-section">';
            preview += '<div class="preview-section-title">Artifact Path:</div>';
            preview += `<code>${escapeHtml(artifact.path)}</code>`;
            preview += '</div>';
            preview += '<div class="preview-section">';
            preview += '<div class="preview-section-title">Size:</div>';
            preview += `${(artifact.size / 1024).toFixed(1)} KB`;
            preview += '</div>';
            preview += '<div class="preview-section">';
            preview += '<em>Use "View Formatted" button for full content preview</em>';
            preview += '</div>';
            preview += '</div>';
            
            return preview;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Load artifact content for preview
        async function loadArtifactPreview(cardId, artifactPath) {
            try {
                // For now, just show metadata - full content loading would require server
                const preview = document.getElementById('preview-' + cardId);
                preview.innerHTML = '<div class="preview-content">Full content preview requires server-side rendering. Use "View Formatted" button for complete view.</div>';
            } catch (e) {
                console.error('Error loading preview:', e);
            }
        }
        
        // Action functions - Fixed to work with file:// protocol
        function openArtifactFile(fullPath) {
            // Convert Windows path to file:// URL
            // Handle Windows backslashes - convert to forward slashes
            let cleanPath = fullPath.replace(/\\\\/g, '/').replace(/\\/g, '/');
            // Remove leading slash if present (file:/// already has it)
            if (cleanPath.startsWith('/')) {
                cleanPath = cleanPath.substring(1);
            }
            // Encode spaces and special characters, but preserve slashes and colons
            const parts = cleanPath.split('/');
            const encodedParts = parts.map(part => {
                // Encode each part separately to preserve slashes
                return encodeURIComponent(part).replace(/%3A/g, ':');
            });
            cleanPath = encodedParts.join('/');
            // Build file:// URL
            const fileUrl = 'file:///' + cleanPath;
            try {
                window.open(fileUrl, '_blank');
            } catch (e) {
                // Fallback: show path for manual opening
                alert('Cannot open file directly.\\n\\nPath: ' + fullPath + '\\n\\nTry opening manually from file explorer.\\n\\nFile URL: ' + fileUrl);
            }
        }
        
        function viewFormattedArtifact(relativePath, artifactType) {
            // Try to open rendered HTML if it exists
            const basePath = window.location.href.substring(0, window.location.href.lastIndexOf('/'));
            const renderedUrl = basePath + '/rendered/' + artifactType + '.html';
            
            // Try to open rendered version
            try {
                const renderedWindow = window.open(renderedUrl, '_blank');
                // Check if it opened successfully after a short delay
                setTimeout(() => {
                    try {
                        if (renderedWindow && !renderedWindow.closed) {
                            // Window opened, might be loading
                            return;
                        }
                    } catch (e) {
                        // Cross-origin check failed, assume it opened
                        return;
                    }
                    // If we get here, show instructions
                    alert('Formatted view not found.\\n\\nTo generate:\\n\\n1. Run: python scripts/temporal__render_artifact.py ' + relativePath + ' --html\\n2. Refresh this page\\n3. Click "View Formatted" again');
                }, 500);
            } catch (e) {
                alert('Cannot open formatted view.\\n\\nTo generate:\\n\\npython scripts/temporal__render_artifact.py ' + relativePath + ' --html');
            }
        }
        
        function viewCodexReview(relativePath) {
            // Open codex_reviews directory
            const basePath = window.location.href.substring(0, window.location.href.lastIndexOf('/'));
            const reviewsDirUrl = basePath + '/codex_reviews/';
            
            try {
                window.open(reviewsDirUrl, '_blank');
                // Show instructions
                setTimeout(() => {
                    alert('Codex Review Directory\\n\\nIf review exists, it will be in the opened directory.\\n\\nTo generate a review:\\n\\npython scripts/temporal__codex_review.py ' + relativePath);
                }, 300);
            } catch (e) {
                alert('Cannot open codex reviews directory.\\n\\nTo generate review:\\n\\npython scripts/temporal__codex_review.py ' + relativePath);
            }
        }
        
        function showDebugInfo(relativePath, metaStr) {
            // Parse meta if it's a string (from JSON.stringify in onclick)
            let meta = {};
            try {
                if (typeof metaStr === 'string') {
                    meta = JSON.parse(metaStr);
                } else {
                    meta = metaStr;
                }
            } catch (e) {
                meta = {};
            }
            
            const debugInfo = {
                artifact_path: relativePath,
                file_path: window.location.href.substring(0, window.location.href.lastIndexOf('/')) + '/' + relativePath,
                metadata: meta,
                timestamp: new Date().toISOString(),
                user_agent: navigator.userAgent,
                protocol: window.location.protocol,
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                }
            };
            
            const infoWindow = window.open('', '_blank');
            const metaJson = JSON.stringify(meta || {}, null, 2);
            infoWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Debug Info: ${relativePath}</title>
                    <style>
                        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 2rem; background: #f5f5f5; max-width: 1200px; margin: 0 auto; }
                        pre { background: white; padding: 1rem; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow-x: auto; font-size: 0.875rem; }
                        h1 { color: #1e40af; margin-bottom: 1rem; }
                        h2 { color: #3b82f6; margin-top: 2rem; margin-bottom: 0.5rem; }
                        .path { color: #666; margin-bottom: 1rem; padding: 0.5rem; background: #eff6ff; border-radius: 4px; }
                        .section { margin-bottom: 1.5rem; }
                        .action-link { display: inline-block; margin: 0.5rem 0.5rem 0.5rem 0; padding: 0.5rem 1rem; background: #3b82f6; color: white; text-decoration: none; border-radius: 4px; }
                        .action-link:hover { background: #2563eb; }
                    </style>
                </head>
                <body>
                    <h1>🐛 Debug Information</h1>
                    <div class="section">
                        <div class="path"><strong>Artifact Path:</strong> ${relativePath}</div>
                    </div>
                    <div class="section">
                        <h2>Metadata</h2>
                        <pre>${metaJson}</pre>
                    </div>
                    <div class="section">
                        <h2>System Info</h2>
                        <pre>${JSON.stringify(debugInfo, null, 2)}</pre>
                    </div>
                    <hr>
                    <div class="section">
                        <h2>Quick Actions</h2>
                        <a href="debug_dashboard/debug_dashboard.html" class="action-link" target="_blank">🔍 Debug Dashboard</a>
                        <a href="rendered/" class="action-link" target="_blank">📄 Rendered Artifacts</a>
                        <a href="codex_reviews/" class="action-link" target="_blank">📝 Codex Reviews</a>
                        <p style="margin-top: 1rem; color: #666; font-size: 0.875rem;">
                            <strong>To generate debug dashboard:</strong><br>
                            python scripts/temporal__debug_dashboard.py
                        </p>
                    </div>
                </body>
                </html>
            `);
            infoWindow.document.close();
        }
    </script>
</body>
</html>"""
    
    return html


def main():
    """Generate artifact index."""
    print("Scanning artifacts directory...")
    artifacts_data = scan_artifacts()
    
    total = sum(len(v) for v in artifacts_data.values())
    print(f"Found {total} artifacts across {len(artifacts_data)} categories")
    
    # Generate JSON index
    index_json = {
        "_meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_artifacts": total,
            "categories": {k: len(v) for k, v in artifacts_data.items()}
        },
        "artifacts": artifacts_data
    }
    
    json_path = OUTPUT_DIR / "ARTIFACT_INDEX.json"
    json_path.write_text(json.dumps(index_json, indent=2), encoding="utf-8")
    print(f"[SUCCESS] JSON index written: {json_path}")
    
    # Generate HTML viewer
    html_content = generate_html_viewer(artifacts_data)
    html_path = OUTPUT_DIR / "ARTIFACT_INDEX.html"
    html_path.write_text(html_content, encoding="utf-8")
    print(f"[SUCCESS] HTML viewer written: {html_path}")
    
    print("\n[SUMMARY]")
    for category, artifacts in artifacts_data.items():
        if artifacts:
            print(f"  {category}: {len(artifacts)} artifacts")
    
    return html_path


if __name__ == "__main__":
    main()
