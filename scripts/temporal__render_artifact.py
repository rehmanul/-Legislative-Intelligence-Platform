"""
Script: temporal__render_artifact.py
Intent: temporal (exploration)

Reads:
- Any artifact JSON file

Writes:
- Human-readable HTML (temporary, for viewing)
- Human-readable Markdown (temporary, for viewing)

Schema:
- HTML/Markdown output with formatted artifact content
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Path setup
BASE_DIR = Path(__file__).parent.parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
OUTPUT_DIR = BASE_DIR / "artifacts" / "rendered"


def load_artifact(artifact_path: Path) -> Optional[Dict[str, Any]]:
    """Load artifact JSON file."""
    try:
        with open(artifact_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Error loading artifact: {e}")
        return None


def render_meta(meta: Dict[str, Any]) -> str:
    """Render _meta block as formatted section."""
    lines = ["## Artifact Metadata\n"]
    
    if "artifact_name" in meta:
        lines.append(f"**Name:** {meta['artifact_name']}\n")
    if "agent_id" in meta:
        lines.append(f"**Agent:** `{meta['agent_id']}`\n")
    if "artifact_type" in meta:
        lines.append(f"**Type:** `{meta['artifact_type']}`\n")
    if "generated_at" in meta:
        lines.append(f"**Generated:** {meta['generated_at']}\n")
    if "status" in meta:
        status_emoji = "✅" if meta['status'] == "ACTIONABLE" else "⚠️"
        lines.append(f"**Status:** {status_emoji} {meta['status']}\n")
    if "confidence" in meta:
        lines.append(f"**Confidence:** {meta['confidence']}\n")
    if "requires_review" in meta and meta.get("requires_review"):
        lines.append(f"**Review Gate:** `{meta['requires_review']}`\n")
    if "human_review_required" in meta:
        lines.append(f"**Review Required:** {'Yes' if meta['human_review_required'] else 'No'}\n")
    
    lines.append("\n---\n\n")
    return "".join(lines)


def render_section(title: str, content: Any, level: int = 2) -> str:
    """Render a section with title and content."""
    heading = "#" * level
    lines = [f"{heading} {title}\n\n"]
    
    if isinstance(content, dict):
        for key, value in content.items():
            if isinstance(value, (dict, list)):
                lines.append(render_section(key.replace("_", " ").title(), value, level + 1))
            else:
                lines.append(f"**{key.replace('_', ' ').title()}:** {value}\n\n")
    elif isinstance(content, list):
        for i, item in enumerate(content, 1):
            if isinstance(item, dict):
                lines.append(f"### Item {i}\n\n")
                for key, value in item.items():
                    if isinstance(value, (dict, list)):
                        lines.append(render_section(key.replace("_", " ").title(), value, level + 2))
                    else:
                        lines.append(f"**{key.replace('_', ' ').title()}:** {value}\n\n")
            else:
                lines.append(f"{i}. {item}\n\n")
    else:
        lines.append(f"{content}\n\n")
    
    return "".join(lines)


def render_artifact_to_markdown(artifact: Dict[str, Any], artifact_path: Path) -> str:
    """Convert artifact JSON to formatted Markdown."""
    lines = []
    
    # Title
    meta = artifact.get("_meta", {})
    artifact_name = meta.get("artifact_name", artifact_path.stem)
    lines.append(f"# {artifact_name}\n\n")
    
    # Metadata section
    if "_meta" in artifact:
        lines.append(render_meta(artifact["_meta"]))
    
    # Render all other sections
    for key, value in artifact.items():
        if key == "_meta":
            continue
        
        section_title = key.replace("_", " ").title()
        lines.append(render_section(section_title, value))
    
    return "".join(lines)


def render_artifact_to_html(artifact: Dict[str, Any], artifact_path: Path) -> str:
    """Convert artifact JSON to formatted HTML."""
    markdown = render_artifact_to_markdown(artifact, artifact_path)
    
    # Simple Markdown to HTML conversion
    html = markdown
    html = html.replace("# ", "<h1>").replace("\n# ", "</h1>\n<h1>")
    html = html.replace("## ", "<h2>").replace("\n## ", "</h2>\n<h2>")
    html = html.replace("### ", "<h3>").replace("\n### ", "</h3>\n<h3>")
    html = html.replace("**", "<strong>").replace("**", "</strong>")
    html = html.replace("`", "<code>").replace("`", "</code>")
    html = html.replace("\n\n", "</p><p>")
    html = html.replace("\n", "<br>")
    
    # Wrap in HTML structure
    meta = artifact.get("_meta", {})
    artifact_name = meta.get("artifact_name", artifact_path.stem)
    
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{artifact_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{
            color: #1e40af;
            border-bottom: 3px solid #3b82f6;
            padding-bottom: 0.5rem;
        }}
        h2 {{
            color: #1e40af;
            margin-top: 2rem;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 0.5rem;
        }}
        h3 {{
            color: #3b82f6;
            margin-top: 1.5rem;
        }}
        code {{
            background: #f3f4f6;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        strong {{
            color: #1e40af;
        }}
        .meta-section {{
            background: #f9fafb;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
            margin: 1rem 0;
        }}
        .status-actionable {{
            color: #065f46;
            background: #d1fae5;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-weight: 500;
        }}
        .status-speculative {{
            color: #92400e;
            background: #fef3c7;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-weight: 500;
        }}
        hr {{
            border: none;
            border-top: 2px solid #e5e7eb;
            margin: 2rem 0;
        }}
    </style>
</head>
<body>
    <p>{html}</p>
</body>
</html>"""
    
    return full_html


def main():
    """Main execution."""
    if len(sys.argv) < 2:
        print("Usage: python temporal__render_artifact.py <artifact_path> [--html|--md]")
        print("\nExample:")
        print("  python temporal__render_artifact.py artifacts/draft_concept_memo_pre_evt/PRE_CONCEPT.json")
        print("  python temporal__render_artifact.py artifacts/draft_concept_memo_pre_evt/PRE_CONCEPT.json --html")
        return None
    
    artifact_path = Path(sys.argv[1])
    if not artifact_path.is_absolute():
        artifact_path = BASE_DIR / artifact_path
    
    if not artifact_path.exists():
        print(f"[ERROR] Artifact not found: {artifact_path}")
        return None
    
    # Load artifact
    artifact = load_artifact(artifact_path)
    if not artifact:
        return None
    
    # Determine output format
    output_format = "both"
    if len(sys.argv) > 2:
        if "--html" in sys.argv:
            output_format = "html"
        elif "--md" in sys.argv:
            output_format = "md"
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate outputs
    artifact_name = artifact_path.stem
    meta = artifact.get("_meta", {})
    artifact_type = meta.get("artifact_type", artifact_name)
    
    outputs = []
    
    if output_format in ("both", "md"):
        markdown = render_artifact_to_markdown(artifact, artifact_path)
        md_path = OUTPUT_DIR / f"{artifact_type}.md"
        md_path.write_text(markdown, encoding='utf-8')
        outputs.append(md_path)
        print(f"[OK] Generated Markdown: {md_path}")
    
    if output_format in ("both", "html"):
        html = render_artifact_to_html(artifact, artifact_path)
        html_path = OUTPUT_DIR / f"{artifact_type}.html"
        html_path.write_text(html, encoding='utf-8')
        outputs.append(html_path)
        print(f"[OK] Generated HTML: {html_path}")
    
    return outputs[0] if outputs else None


if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n[SUCCESS] Artifact rendered successfully!")
        print(f"View at: {result}")
    else:
        sys.exit(1)
