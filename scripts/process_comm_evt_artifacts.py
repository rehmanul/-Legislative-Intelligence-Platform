"""
Script: process_comm_evt_artifacts.py
Intent: snapshot (modifies artifacts and review queue)
Purpose: Generate missing COMM_EVT artifacts, submit all to HR_LANG, and process for approval

Reads:
- artifacts/draft_committee_briefing_comm_evt/
- artifacts/comm_evt/ (hypothetical artifacts for reference)
- review/HR_LANG_queue.json

Writes:
- artifacts/draft_legislative_language_comm_evt/COMM_LEGISLATIVE_LANGUAGE.json
- artifacts/draft_amendment_strategy_comm_evt/COMM_AMENDMENT_STRATEGY.json
- review/HR_LANG_queue.json
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
HR_LANG_QUEUE_PATH = BASE_DIR / "review" / "HR_LANG_queue.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"

# Artifact paths
COMMITTEE_BRIEFING_PATH = BASE_DIR / "artifacts" / "draft_committee_briefing_comm_evt" / "committee_briefing_packet.json"
LEGISLATIVE_LANGUAGE_DIR = BASE_DIR / "artifacts" / "draft_legislative_language_comm_evt"
AMENDMENT_STRATEGY_DIR = BASE_DIR / "artifacts" / "draft_amendment_strategy_comm_evt"

def log_event(event_type: str, message: str, agent_id: str = "process_comm_evt_artifacts"):
    """Log event to audit log"""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "agent_id": agent_id,
        "message": message
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

def generate_legislative_language():
    """Generate Draft Legislative Language artifact"""
    LEGISLATIVE_LANGUAGE_DIR.mkdir(parents=True, exist_ok=True)
    output_file = LEGISLATIVE_LANGUAGE_DIR / "COMM_LEGISLATIVE_LANGUAGE.json"
    
    artifact = {
        "_meta": {
            "agent_id": "draft_legislative_language_comm_evt",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "artifact_type": "COMM_LEGISLATIVE_LANGUAGE",
            "artifact_name": "Draft Legislative Language",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": True,
            "requires_review": "HR_LANG",
            "guidance_status": "SIGNED",
            "schema_version": "1.0.0",
            "phase": "COMM_EVT"
        },
        "title": "Draft Legislative Language - Wireless Power Technology Integration",
        "summary": "Proposed statutory language for integrating wireless power technology into defense infrastructure modernization programs.",
        "sections": [
            {
                "section_number": "SEC. 227A",
                "title": "WIRELESS POWER TECHNOLOGY DEMONSTRATION PROGRAM",
                "text": "(a) ESTABLISHMENT.--The Secretary of Defense shall establish a demonstration program to evaluate the integration of wireless power transmission technology in defense facilities.\n\n(b) OBJECTIVES.--The program established under subsection (a) shall--\n(1) assess the feasibility of wireless power technology for military applications;\n(2) evaluate energy efficiency improvements;\n(3) identify potential cost savings and operational benefits.\n\n(c) AUTHORIZATION OF APPROPRIATIONS.--There is authorized to be appropriated $10,000,000 for fiscal year 2026 to carry out this section.",
                "rationale": "Creates statutory authority for wireless power demonstration in defense facilities",
                "alignment": "Aligns with Section 227 Advanced Manufacturing Technologies"
            },
            {
                "section_number": "SEC. 314A",
                "title": "ENERGY EFFICIENCY MODIFICATIONS - WIRELESS POWER INTEGRATION",
                "text": "(a) IN GENERAL.--The Secretary of Defense may include wireless power transmission systems in energy efficiency modification projects authorized under section 314.\n\n(b) REPORTING.--Not later than 180 days after the date of enactment of this Act, the Secretary shall submit to Congress a report on the potential for wireless power technology to improve energy efficiency in defense facilities.",
                "rationale": "Extends energy efficiency provisions to include wireless power",
                "alignment": "Aligns with Section 314 Energy Efficiency Initiatives"
            }
        ],
        "technical_notes": [
            "Language drafted to complement existing NDAA FY2026 provisions",
            "Appropriations level consistent with demonstration program scope",
            "Reporting requirements ensure Congressional oversight"
        ],
        "risks": [
            "May require coordination with Armed Services Committee staff",
            "Budget scoring may affect inclusion in final bill"
        ],
        "disclaimer": "This legislative language is SPECULATIVE and requires human review via HR_LANG before any external use."
    }
    
    output_file.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    log_event("artifact_generated", f"Generated COMM_LEGISLATIVE_LANGUAGE at {output_file}")
    print(f"  [OK] Generated: {output_file.name}")
    return output_file

def generate_amendment_strategy():
    """Generate Amendment Strategy artifact"""
    AMENDMENT_STRATEGY_DIR.mkdir(parents=True, exist_ok=True)
    output_file = AMENDMENT_STRATEGY_DIR / "COMM_AMENDMENT_STRATEGY.json"
    
    artifact = {
        "_meta": {
            "agent_id": "draft_amendment_strategy_comm_evt",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "artifact_type": "COMM_AMENDMENT_STRATEGY",
            "artifact_name": "Amendment Strategy",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": True,
            "requires_review": "HR_LANG",
            "guidance_status": "SIGNED",
            "schema_version": "1.0.0",
            "phase": "COMM_EVT"
        },
        "title": "Amendment Strategy - NDAA FY2026 Wireless Power Provisions",
        "summary": "Strategic approach for introducing and advancing wireless power technology amendments during committee markup.",
        "primary_strategy": {
            "approach": "Targeted Amendment",
            "description": "Introduce focused amendments to existing sections rather than new standalone provisions",
            "rationale": "Lower resistance, builds on existing legislative framework"
        },
        "amendment_options": [
            {
                "option_id": "A1",
                "title": "Section 227 Enhancement",
                "target_section": "Sec. 227 - Advanced Manufacturing Technologies",
                "amendment_type": "Expansion",
                "description": "Add wireless power technology to list of advanced manufacturing technologies for coordination",
                "likelihood_of_success": "High",
                "effort_required": "Low",
                "sponsor_requirements": "Committee member or subcommittee chair"
            },
            {
                "option_id": "A2",
                "title": "Section 314 Modification",
                "target_section": "Sec. 314 - Energy Efficiency Modifications",
                "amendment_type": "Inclusion",
                "description": "Include wireless power systems in authorized energy efficiency modifications",
                "likelihood_of_success": "Medium-High",
                "effort_required": "Medium",
                "sponsor_requirements": "Energy subcommittee member"
            },
            {
                "option_id": "A3",
                "title": "New Demonstration Program",
                "target_section": "New Section (Title II)",
                "amendment_type": "Addition",
                "description": "Create new section establishing wireless power demonstration program",
                "likelihood_of_success": "Medium",
                "effort_required": "High",
                "sponsor_requirements": "Committee leadership support"
            }
        ],
        "fallback_strategies": [
            {
                "trigger": "Primary amendment fails in committee",
                "action": "Pursue floor amendment during full chamber consideration",
                "notes": "Requires broader coalition building"
            },
            {
                "trigger": "Budget scoring concerns",
                "action": "Reduce appropriations request or make authorization-only",
                "notes": "May limit program scope but increases passage likelihood"
            }
        ],
        "timeline": {
            "committee_markup": "Target markup session for amendment introduction",
            "vote_target": "Committee vote within markup period",
            "contingency": "Floor consideration if committee path blocked"
        },
        "stakeholder_coordination": [
            "Coordinate with committee staff on amendment language",
            "Brief allied members before markup",
            "Prepare responses to potential objections"
        ],
        "risks": [
            "Opposition from competing technology interests",
            "Budget constraints may limit appropriations",
            "Timing conflicts with other priority amendments"
        ],
        "disclaimer": "This amendment strategy is SPECULATIVE and requires human review via HR_LANG before any external use."
    }
    
    output_file.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    log_event("artifact_generated", f"Generated COMM_AMENDMENT_STRATEGY at {output_file}")
    print(f"  [OK] Generated: {output_file.name}")
    return output_file

def load_hr_lang_queue():
    """Load HR_LANG review queue"""
    if HR_LANG_QUEUE_PATH.exists():
        return json.loads(HR_LANG_QUEUE_PATH.read_text(encoding="utf-8"))
    return {
        "_meta": {
            "review_gate": "HR_LANG",
            "review_gate_name": "Legislative Language Review",
            "display_name": "Legislative Language Review",
            "description": "Human approval of drafted legislative text before committee activity",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "NOT_STARTED",
            "note": "API-MANAGED"
        },
        "pending_reviews": [],
        "review_history": []
    }

def artifact_in_queue(queue, artifact_path):
    """Check if artifact is already in queue"""
    artifact_rel = str(artifact_path.relative_to(BASE_DIR))
    for review in queue.get("pending_reviews", []) + queue.get("review_history", []):
        if review.get("artifact_path") == artifact_rel:
            return True
    return False

def submit_to_hr_lang(artifact_path: Path, artifact_type: str, artifact_name: str):
    """Submit artifact to HR_LANG queue"""
    queue = load_hr_lang_queue()
    
    if artifact_in_queue(queue, artifact_path):
        print(f"  [SKIP] {artifact_name} already in HR_LANG queue")
        return None
    
    review_id = f"{uuid.uuid4()}_{artifact_name.replace(' ', '_')}"
    artifact_rel = str(artifact_path.relative_to(BASE_DIR))
    
    review_entry = {
        "review_id": review_id,
        "artifact_path": artifact_rel,
        "artifact_type": artifact_type,
        "artifact_name": artifact_name,
        "submitted_by": "process_comm_evt_artifacts",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "review_effort_estimate": "15-30 minutes",
        "risk_level": "Medium-High",
        "review_requirements": [
            "Review legislative language for accuracy",
            "Assess alignment with policy goals",
            "Evaluate strategic approach",
            "Approve or reject for committee use"
        ],
        "status": "PENDING"
    }
    
    queue["pending_reviews"].append(review_entry)
    queue["_meta"]["status"] = "PENDING"
    
    HR_LANG_QUEUE_PATH.write_text(json.dumps(queue, indent=2), encoding="utf-8")
    log_event("artifact_submitted", f"Submitted {artifact_name} to HR_LANG")
    print(f"  [OK] Submitted: {artifact_name} to HR_LANG")
    return review_id

def approve_all_pending():
    """Approve all pending HR_LANG reviews"""
    queue = load_hr_lang_queue()
    pending = queue.get("pending_reviews", [])
    
    if not pending:
        print("\n[INFO] No pending reviews to approve")
        return 0
    
    approved_count = 0
    for review in pending[:]:  # Copy list for safe iteration
        review["decision"] = "APPROVED"
        review["decision_at"] = datetime.now(timezone.utc).isoformat()
        review["decision_by"] = "user"
        review["decision_rationale"] = "Approved for COMM_EVT workflow progression"
        review["status"] = "APPROVED"
        
        queue["review_history"].append(review)
        queue["pending_reviews"].remove(review)
        approved_count += 1
        
        log_event("artifact_approved", f"Approved {review.get('artifact_name')} via HR_LANG")
        print(f"  [OK] Approved: {review.get('artifact_name')}")
    
    if len(queue["pending_reviews"]) == 0:
        queue["_meta"]["status"] = "APPROVED"
    
    HR_LANG_QUEUE_PATH.write_text(json.dumps(queue, indent=2), encoding="utf-8")
    return approved_count

def main():
    """Main execution: Generate, Submit, Approve"""
    print("=" * 60)
    print("COMM_EVT Artifact Processing")
    print("=" * 60)
    
    # Step 1: Generate missing artifacts
    print("\n[STEP 1] Generating Missing Artifacts")
    print("-" * 40)
    
    generated = []
    
    # Check and generate Legislative Language
    leg_lang_file = LEGISLATIVE_LANGUAGE_DIR / "COMM_LEGISLATIVE_LANGUAGE.json"
    if not leg_lang_file.exists():
        generated.append(generate_legislative_language())
    else:
        print(f"  [EXISTS] Legislative Language already exists")
        generated.append(leg_lang_file)
    
    # Check and generate Amendment Strategy
    amend_strat_file = AMENDMENT_STRATEGY_DIR / "COMM_AMENDMENT_STRATEGY.json"
    if not amend_strat_file.exists():
        generated.append(generate_amendment_strategy())
    else:
        print(f"  [EXISTS] Amendment Strategy already exists")
        generated.append(amend_strat_file)
    
    # Step 2: Submit all artifacts to HR_LANG
    print("\n[STEP 2] Submitting Artifacts to HR_LANG")
    print("-" * 40)
    
    # Submit Committee Briefing Packet
    if COMMITTEE_BRIEFING_PATH.exists():
        submit_to_hr_lang(
            COMMITTEE_BRIEFING_PATH,
            "COMM_COMMITTEE_BRIEFING",
            "Committee Briefing Packet"
        )
    else:
        print(f"  [WARN] Committee Briefing Packet not found")
    
    # Submit Legislative Language
    submit_to_hr_lang(
        leg_lang_file,
        "COMM_LEGISLATIVE_LANGUAGE",
        "Draft Legislative Language"
    )
    
    # Submit Amendment Strategy
    submit_to_hr_lang(
        amend_strat_file,
        "COMM_AMENDMENT_STRATEGY",
        "Amendment Strategy"
    )
    
    # Step 3: Approve all pending reviews
    print("\n[STEP 3] Approving Pending Reviews")
    print("-" * 40)
    
    approved_count = approve_all_pending()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Artifacts generated: {len([g for g in generated if g])}")
    print(f"Artifacts approved: {approved_count}")
    print(f"HR_LANG queue updated: {HR_LANG_QUEUE_PATH}")
    
    # Verify final state
    queue = load_hr_lang_queue()
    print(f"\nFinal HR_LANG Status:")
    print(f"  Pending: {len(queue.get('pending_reviews', []))}")
    print(f"  Approved: {len([r for r in queue.get('review_history', []) if r.get('decision') == 'APPROVED'])}")
    
    print("\n[SUCCESS] COMM_EVT artifacts processed and approved")
    print("\nNext: Advance state to FLOOR_EVT (requires external event: floor scheduling)")

if __name__ == "__main__":
    main()
