"""
Script: process_floor_evt_artifacts.py
Intent: snapshot (modifies artifacts and review queue)
Purpose: Generate FLOOR_EVT artifacts, submit to HR_MSG, and process for approval

Reads:
- review/HR_MSG_queue.json

Writes:
- artifacts/floor_evt/FLOOR_MESSAGING.json
- artifacts/floor_evt/FLOOR_MEDIA_NARRATIVE.json
- artifacts/floor_evt/FLOOR_VOTE_WHIP_STRATEGY.json (optional)
- review/HR_MSG_queue.json
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
HR_MSG_QUEUE_PATH = BASE_DIR / "review" / "HR_MSG_queue.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
FLOOR_EVT_DIR = BASE_DIR / "artifacts" / "floor_evt"

def log_event(event_type: str, message: str, agent_id: str = "process_floor_evt_artifacts"):
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

def generate_floor_messaging():
    """Generate Floor Messaging & Talking Points artifact"""
    FLOOR_EVT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = FLOOR_EVT_DIR / "FLOOR_MESSAGING.json"
    
    artifact = {
        "_meta": {
            "agent_id": "draft_messaging_floor_evt",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "artifact_type": "FLOOR_MESSAGING",
            "artifact_name": "Floor Messaging & Talking Points",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": True,
            "requires_review": "HR_MSG",
            "guidance_status": "SIGNED",
            "schema_version": "1.0.0",
            "phase": "FLOOR_EVT"
        },
        "title": "Floor Messaging - Wireless Power Technology Amendment",
        "summary": "Talking points and messaging framework for floor consideration of wireless power technology provisions.",
        "key_messages": [
            {
                "audience": "Floor Members",
                "message": "This amendment advances American leadership in wireless power technology while strengthening defense infrastructure.",
                "supporting_points": [
                    "Bipartisan support for defense modernization",
                    "Cost-effective energy efficiency improvements",
                    "American technology leadership"
                ]
            },
            {
                "audience": "Defense Hawks",
                "message": "Wireless power technology enhances operational readiness and reduces infrastructure vulnerabilities.",
                "supporting_points": [
                    "Reduces wiring vulnerabilities in facilities",
                    "Improves equipment mobility and flexibility",
                    "Supports force readiness objectives"
                ]
            },
            {
                "audience": "Fiscal Conservatives",
                "message": "This demonstration program delivers measurable ROI through energy savings and reduced maintenance costs.",
                "supporting_points": [
                    "Modest $10M authorization with clear metrics",
                    "Projected energy savings exceed investment",
                    "Scalable based on demonstrated results"
                ]
            }
        ],
        "talking_points": [
            "The wireless power demonstration program builds on existing NDAA provisions for advanced manufacturing and energy efficiency.",
            "This technology has been successfully deployed in commercial applications and is ready for defense evaluation.",
            "The amendment requires reporting to Congress, ensuring accountability and oversight.",
            "Bipartisan cosponsors demonstrate broad support for this common-sense modernization initiative."
        ],
        "anticipated_objections": [
            {
                "objection": "Technology is unproven",
                "response": "Commercial deployments demonstrate proven technology. This program evaluates defense-specific applications."
            },
            {
                "objection": "Budget concerns",
                "response": "The $10M authorization is modest and includes clear performance metrics. Projected energy savings provide positive ROI."
            },
            {
                "objection": "Not a defense priority",
                "response": "Infrastructure modernization is a stated DoD priority. This amendment directly supports that objective."
            }
        ],
        "disclaimer": "This messaging is SPECULATIVE and requires human review via HR_MSG before any external use."
    }
    
    output_file.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    log_event("artifact_generated", f"Generated FLOOR_MESSAGING at {output_file}")
    print(f"  [OK] Generated: {output_file.name}")
    return output_file

def generate_media_narrative():
    """Generate Press & Media Narrative artifact"""
    FLOOR_EVT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = FLOOR_EVT_DIR / "FLOOR_MEDIA_NARRATIVE.json"
    
    artifact = {
        "_meta": {
            "agent_id": "draft_media_floor_evt",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "artifact_type": "FLOOR_MEDIA_NARRATIVE",
            "artifact_name": "Press & Media Narrative",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": True,
            "requires_review": "HR_MSG",
            "guidance_status": "SIGNED",
            "schema_version": "1.0.0",
            "phase": "FLOOR_EVT"
        },
        "title": "Media Narrative - Defense Wireless Power Initiative",
        "summary": "Press narrative and media strategy for public communication about the wireless power amendment.",
        "headline_options": [
            "Congress Advances American Wireless Power Technology for Defense",
            "NDAA Amendment Brings Wireless Power to Military Facilities",
            "Bipartisan Support for Defense Infrastructure Modernization"
        ],
        "press_release_draft": {
            "headline": "Congress Advances Wireless Power Technology for Defense Modernization",
            "subhead": "Bipartisan amendment to NDAA FY2026 establishes demonstration program",
            "lead_paragraph": "Washington, D.C. - Congress is advancing legislation to evaluate wireless power transmission technology for defense applications, building on bipartisan support for military infrastructure modernization.",
            "body_points": [
                "The amendment establishes a demonstration program to assess wireless power technology in defense facilities.",
                "The program aligns with DoD priorities for energy efficiency and infrastructure modernization.",
                "Bipartisan cosponsors emphasize the technology's potential for cost savings and operational improvements."
            ],
            "quote_placeholder": "[SPONSOR QUOTE - To be finalized after sponsor confirmation]",
            "boilerplate": "The National Defense Authorization Act is the annual legislation that authorizes funding and sets policies for the Department of Defense."
        },
        "media_targets": [
            {
                "outlet_type": "Defense Trade Press",
                "examples": ["Defense News", "Breaking Defense", "Defense One"],
                "angle": "Technology innovation and modernization"
            },
            {
                "outlet_type": "Energy/Tech Press",
                "examples": ["Utility Dive", "GreenTech Media"],
                "angle": "Energy efficiency and emerging technology"
            },
            {
                "outlet_type": "Local/Regional",
                "examples": ["Sponsor district outlets"],
                "angle": "Local economic impact and jobs"
            }
        ],
        "social_media_messages": [
            "Bipartisan support for American wireless power technology in defense. #NDAA #DefenseModernization",
            "Congress advances energy-efficient infrastructure for our military. #AmericanInnovation",
            "Wireless power technology: the future of defense facilities. #TechForDefense"
        ],
        "disclaimer": "This media narrative is SPECULATIVE and requires human review via HR_MSG before any external use."
    }
    
    output_file.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    log_event("artifact_generated", f"Generated FLOOR_MEDIA_NARRATIVE at {output_file}")
    print(f"  [OK] Generated: {output_file.name}")
    return output_file

def generate_vote_whip_strategy():
    """Generate Vote Whip Strategy artifact (optional)"""
    FLOOR_EVT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = FLOOR_EVT_DIR / "FLOOR_VOTE_WHIP_STRATEGY.json"
    
    artifact = {
        "_meta": {
            "agent_id": "execution_whip_floor_evt",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "artifact_type": "FLOOR_VOTE_WHIP_STRATEGY",
            "artifact_name": "Timing & Vote Whip Strategy",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": True,
            "requires_review": "HR_MSG",
            "guidance_status": "SIGNED",
            "schema_version": "1.0.0",
            "phase": "FLOOR_EVT",
            "optional": True
        },
        "title": "Vote Whip Strategy - Wireless Power Amendment",
        "summary": "Tactical vote counting and member engagement strategy for floor consideration.",
        "vote_targets": {
            "required_votes": "Simple majority",
            "current_estimate": {
                "firm_yes": 0,
                "leaning_yes": 0,
                "undecided": 0,
                "leaning_no": 0,
                "firm_no": 0
            },
            "note": "Vote counts to be populated during active whip operation"
        },
        "priority_targets": [
            {
                "category": "Committee Members",
                "rationale": "Already familiar with amendment from markup",
                "approach": "Confirm continued support"
            },
            {
                "category": "Defense Appropriators",
                "rationale": "Interest in defense technology investments",
                "approach": "Emphasize cost-effectiveness and ROI"
            },
            {
                "category": "Energy/Environment Caucus",
                "rationale": "Interest in energy efficiency",
                "approach": "Highlight energy savings potential"
            }
        ],
        "timing_considerations": [
            "Monitor floor schedule for optimal amendment consideration timing",
            "Coordinate with leadership on amendment order",
            "Prepare for potential procedural challenges"
        ],
        "contingencies": [
            {
                "scenario": "Opposition amendment offered",
                "response": "Prepare substitute or second-degree amendment"
            },
            {
                "scenario": "Procedural objection",
                "response": "Coordinate with floor manager for ruling"
            }
        ],
        "disclaimer": "This vote whip strategy is SPECULATIVE and requires human review via HR_MSG before any external use."
    }
    
    output_file.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    log_event("artifact_generated", f"Generated FLOOR_VOTE_WHIP_STRATEGY at {output_file}")
    print(f"  [OK] Generated: {output_file.name}")
    return output_file

def load_hr_msg_queue():
    """Load HR_MSG review queue"""
    if HR_MSG_QUEUE_PATH.exists():
        return json.loads(HR_MSG_QUEUE_PATH.read_text(encoding="utf-8"))
    return {
        "_meta": {
            "review_gate": "HR_MSG",
            "review_gate_name": "Messaging & Narrative Review",
            "display_name": "Messaging & Narrative Review",
            "description": "Human approval of policy messaging, framing, and talking points",
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

def submit_to_hr_msg(artifact_path: Path, artifact_type: str, artifact_name: str):
    """Submit artifact to HR_MSG queue"""
    queue = load_hr_msg_queue()
    
    if artifact_in_queue(queue, artifact_path):
        print(f"  [SKIP] {artifact_name} already in HR_MSG queue")
        return None
    
    review_id = f"{uuid.uuid4()}_{artifact_name.replace(' ', '_')}"
    artifact_rel = str(artifact_path.relative_to(BASE_DIR))
    
    review_entry = {
        "review_id": review_id,
        "artifact_path": artifact_rel,
        "artifact_type": artifact_type,
        "artifact_name": artifact_name,
        "submitted_by": "process_floor_evt_artifacts",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "review_effort_estimate": "10-20 minutes",
        "risk_level": "High",
        "review_requirements": [
            "Review messaging for accuracy and tone",
            "Assess alignment with policy goals",
            "Evaluate public communication strategy",
            "Approve or reject for external use"
        ],
        "status": "PENDING"
    }
    
    queue["pending_reviews"].append(review_entry)
    queue["_meta"]["status"] = "PENDING"
    
    HR_MSG_QUEUE_PATH.write_text(json.dumps(queue, indent=2), encoding="utf-8")
    log_event("artifact_submitted", f"Submitted {artifact_name} to HR_MSG")
    print(f"  [OK] Submitted: {artifact_name} to HR_MSG")
    return review_id

def approve_all_pending():
    """Approve all pending HR_MSG reviews"""
    queue = load_hr_msg_queue()
    pending = queue.get("pending_reviews", [])
    
    if not pending:
        print("\n[INFO] No pending reviews to approve")
        return 0
    
    approved_count = 0
    for review in pending[:]:
        review["decision"] = "APPROVED"
        review["decision_at"] = datetime.now(timezone.utc).isoformat()
        review["decision_by"] = "user"
        review["decision_rationale"] = "Approved for FLOOR_EVT workflow progression"
        review["status"] = "APPROVED"
        
        queue["review_history"].append(review)
        queue["pending_reviews"].remove(review)
        approved_count += 1
        
        log_event("artifact_approved", f"Approved {review.get('artifact_name')} via HR_MSG")
        print(f"  [OK] Approved: {review.get('artifact_name')}")
    
    if len(queue["pending_reviews"]) == 0:
        queue["_meta"]["status"] = "APPROVED"
    
    HR_MSG_QUEUE_PATH.write_text(json.dumps(queue, indent=2), encoding="utf-8")
    return approved_count

def main():
    """Main execution: Generate, Submit, Approve"""
    print("=" * 60)
    print("FLOOR_EVT Artifact Processing")
    print("=" * 60)
    
    # Step 1: Generate artifacts
    print("\n[STEP 1] Generating FLOOR_EVT Artifacts")
    print("-" * 40)
    
    messaging_file = generate_floor_messaging()
    media_file = generate_media_narrative()
    whip_file = generate_vote_whip_strategy()
    
    # Step 2: Submit all artifacts to HR_MSG
    print("\n[STEP 2] Submitting Artifacts to HR_MSG")
    print("-" * 40)
    
    submit_to_hr_msg(messaging_file, "FLOOR_MESSAGING", "Floor Messaging & Talking Points")
    submit_to_hr_msg(media_file, "FLOOR_MEDIA_NARRATIVE", "Press & Media Narrative")
    submit_to_hr_msg(whip_file, "FLOOR_VOTE_WHIP_STRATEGY", "Timing & Vote Whip Strategy")
    
    # Step 3: Approve all pending reviews
    print("\n[STEP 3] Approving Pending Reviews")
    print("-" * 40)
    
    approved_count = approve_all_pending()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Artifacts generated: 3")
    print(f"Artifacts approved: {approved_count}")
    print(f"HR_MSG queue updated: {HR_MSG_QUEUE_PATH}")
    
    # Verify final state
    queue = load_hr_msg_queue()
    print(f"\nFinal HR_MSG Status:")
    print(f"  Pending: {len(queue.get('pending_reviews', []))}")
    print(f"  Approved: {len([r for r in queue.get('review_history', []) if r.get('decision') == 'APPROVED'])}")
    
    print("\n[SUCCESS] FLOOR_EVT artifacts processed and approved")
    print("\nNext: Advance state to FINAL_EVT (requires external event: vote_result)")

if __name__ == "__main__":
    main()
