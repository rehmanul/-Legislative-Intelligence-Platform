"""
Script: temporal__codex_review.py
Intent: temporal (exploration)

Reads:
- Human artifacts (policy docs, concept memos, markdown files)
- JSON artifacts (converted to text first)

Writes:
- Review report (temporary, for viewing)

Schema:
- Review report with Codex feedback
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Path setup
BASE_DIR = Path(__file__).parent.parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
OUTPUT_DIR = BASE_DIR / "artifacts" / "codex_reviews"


def load_artifact_content(artifact_path: Path) -> Optional[str]:
    """Load artifact content as text."""
    try:
        if artifact_path.suffix == ".json":
            with open(artifact_path, 'r', encoding='utf-8') as f:
                artifact = json.load(f)
            
            # Convert JSON to readable text
            lines = []
            meta = artifact.get("_meta", {})
            lines.append(f"# {meta.get('artifact_name', artifact_path.stem)}\n\n")
            lines.append("## Metadata\n\n")
            for key, value in meta.items():
                lines.append(f"- **{key}:** {value}\n")
            lines.append("\n## Content\n\n")
            
            # Convert main content
            for key, value in artifact.items():
                if key == "_meta":
                    continue
                lines.append(f"### {key.replace('_', ' ').title()}\n\n")
                if isinstance(value, (dict, list)):
                    lines.append(json.dumps(value, indent=2))
                else:
                    lines.append(str(value))
                lines.append("\n\n")
            
            return "".join(lines)
        else:
            # Read as text
            return artifact_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"[ERROR] Error loading artifact: {e}")
        return None


def format_codex_review_request(content: str, artifact_path: Path) -> str:
    """Format content for Codex review."""
    artifact_name = artifact_path.stem
    
    prompt = f"""Please review the following artifact and provide structured feedback:

**Artifact:** {artifact_name}
**Path:** {artifact_path.relative_to(BASE_DIR)}

**Review Focus Areas:**
1. Clarity and readability
2. Completeness and structure
3. Accuracy and consistency
4. Actionability and recommendations
5. Areas for improvement

**Artifact Content:**

{content}

**Please provide:**
- Summary of key strengths
- Areas that need improvement
- Specific recommendations
- Priority issues (if any)
- Overall assessment
"""
    return prompt


def generate_codex_review(content: str, artifact_path: Path) -> Dict[str, Any]:
    """
    Generate Codex review (simulated - replace with actual Codex API call).
    
    In production, this would call the Codex API. For now, it generates
    a structured review based on content analysis.
    """
    # Simulated review - replace with actual Codex API integration
    review = {
        "review_id": f"codex_review_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "artifact_path": str(artifact_path.relative_to(BASE_DIR)),
        "artifact_name": artifact_path.stem,
        "reviewed_at": datetime.utcnow().isoformat() + "Z",
        "reviewer": "codex",
        "summary": {
            "overall_assessment": "Content review generated",
            "strength_score": "N/A",
            "improvement_priority": "medium"
        },
        "strengths": [
            "Artifact structure is clear",
            "Metadata is well-organized",
            "Content follows expected format"
        ],
        "improvements": [
            "Consider adding more specific examples",
            "Enhance clarity in technical sections",
            "Expand on recommendations"
        ],
        "recommendations": [
            "Review for completeness",
            "Verify all claims are supported",
            "Ensure actionable next steps are clear"
        ],
        "priority_issues": [],
        "notes": "This is a simulated review. Replace with actual Codex API integration for production use."
    }
    
    # Basic content analysis
    word_count = len(content.split())
    has_meta = "_meta" in content or "metadata" in content.lower()
    has_recommendations = "recommend" in content.lower() or "next step" in content.lower()
    
    if word_count < 500:
        review["improvements"].append("Content may be too brief - consider expanding")
    
    if not has_meta:
        review["improvements"].append("Missing metadata section")
    
    if not has_recommendations:
        review["improvements"].append("Consider adding actionable recommendations")
    
    return review


def render_review_report(review: Dict[str, Any]) -> str:
    """Render review as formatted Markdown report."""
    lines = []
    
    lines.append(f"# Codex Review: {review['artifact_name']}\n\n")
    lines.append(f"**Reviewed:** {review['reviewed_at']}\n")
    lines.append(f"**Reviewer:** {review['reviewer']}\n")
    lines.append(f"**Artifact:** `{review['artifact_path']}`\n\n")
    lines.append("---\n\n")
    
    # Summary
    lines.append("## Summary\n\n")
    summary = review.get("summary", {})
    lines.append(f"**Overall Assessment:** {summary.get('overall_assessment', 'N/A')}\n")
    lines.append(f"**Improvement Priority:** {summary.get('improvement_priority', 'N/A')}\n\n")
    
    # Strengths
    if review.get("strengths"):
        lines.append("## Strengths\n\n")
        for strength in review["strengths"]:
            lines.append(f"- ✅ {strength}\n")
        lines.append("\n")
    
    # Improvements
    if review.get("improvements"):
        lines.append("## Areas for Improvement\n\n")
        for improvement in review["improvements"]:
            lines.append(f"- ⚠️ {improvement}\n")
        lines.append("\n")
    
    # Recommendations
    if review.get("recommendations"):
        lines.append("## Recommendations\n\n")
        for rec in review["recommendations"]:
            lines.append(f"- 💡 {rec}\n")
        lines.append("\n")
    
    # Priority Issues
    if review.get("priority_issues"):
        lines.append("## Priority Issues\n\n")
        for issue in review["priority_issues"]:
            lines.append(f"- 🔴 {issue}\n")
        lines.append("\n")
    
    # Notes
    if review.get("notes"):
        lines.append("## Notes\n\n")
        lines.append(f"{review['notes']}\n\n")
    
    return "".join(lines)


def main():
    """Main execution."""
    if len(sys.argv) < 2:
        print("Usage: python temporal__codex_review.py <artifact_path>")
        print("\nExample:")
        print("  python temporal__codex_review.py artifacts/draft_concept_memo_pre_evt/PRE_CONCEPT.json")
        print("  python temporal__codex_review.py artifacts/policy/key_findings.md")
        return None
    
    artifact_path = Path(sys.argv[1])
    if not artifact_path.is_absolute():
        artifact_path = BASE_DIR / artifact_path
    
    if not artifact_path.exists():
        print(f"[ERROR] Artifact not found: {artifact_path}")
        return None
    
    # Load content
    content = load_artifact_content(artifact_path)
    if not content:
        return None
    
    # Generate review
    print(f"[INFO] Generating Codex review for: {artifact_path.name}")
    review = generate_codex_review(content, artifact_path)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save review JSON
    review_json_path = OUTPUT_DIR / f"{review['review_id']}.json"
    review_json_path.write_text(json.dumps(review, indent=2), encoding='utf-8')
    print(f"[OK] Review JSON saved: {review_json_path}")
    
    # Save review report
    report = render_review_report(review)
    report_path = OUTPUT_DIR / f"{review['review_id']}.md"
    report_path.write_text(report, encoding='utf-8')
    print(f"[OK] Review report saved: {report_path}")
    
    # Print summary
    print(f"\n[SUMMARY] Review Summary:")
    print(f"   Overall: {review['summary']['overall_assessment']}")
    print(f"   Strengths: {len(review.get('strengths', []))}")
    print(f"   Improvements: {len(review.get('improvements', []))}")
    print(f"   Recommendations: {len(review.get('recommendations', []))}")
    
    return report_path


if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n[SUCCESS] Codex review completed!")
        print(f"View report at: {result}")
    else:
        sys.exit(1)
