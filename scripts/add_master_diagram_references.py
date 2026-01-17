"""
Script: add_master_diagram_references.py
Intent: snapshot (modifies files)
Purpose: Add master diagram reference to all .mmd files that don't have it

Reads:
- agent-orchestrator/**/*.mmd files

Writes:
- Updates .mmd files with master diagram reference

Schema: N/A (file modification script)
"""

import re
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).parent.parent
MASTER_REF = "%% Master Diagram Reference: .userInput/agent orchestrator 1.6.mmd\n%% This diagram is a specialized view derived from the master diagram\n"
MASTER_REF_PATTERNS = [
    r"agent orchestrator 1\.6\.mmd",
    r"agent orchestrator 1\.6",
    r"%% Master Diagram Reference",
    r"Master Diagram Reference"
]

def has_master_reference(content: str) -> bool:
    """Check if content already has master diagram reference"""
    for pattern in MASTER_REF_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False

def add_reference_to_file(file_path: Path) -> bool:
    """Add master diagram reference to file if missing"""
    try:
        content = file_path.read_text(encoding="utf-8")
        
        if has_master_reference(content):
            return False  # Already has reference
        
        # Determine where to add reference
        lines = content.split("\n")
        
        # If file starts with config block, add after it
        if lines[0].strip() == "---" and len(lines) > 1 and lines[1].strip().startswith("config"):
            # Find end of config block
            config_end = 0
            for i, line in enumerate(lines):
                if i > 0 and line.strip() == "---":
                    config_end = i + 1
                    break
            
            # Insert reference after config block
            new_lines = lines[:config_end] + [MASTER_REF.rstrip()] + lines[config_end:]
            file_path.write_text("\n".join(new_lines), encoding="utf-8")
            return True
        
        # If file starts with comment, add before first non-comment line
        elif lines[0].strip().startswith("%%"):
            # Find first non-comment line
            first_non_comment = 0
            for i, line in enumerate(lines):
                if not line.strip().startswith("%%") and line.strip() and not line.strip().startswith("---"):
                    first_non_comment = i
                    break
            
            # Insert reference before first non-comment
            new_lines = lines[:first_non_comment] + [MASTER_REF.rstrip()] + lines[first_non_comment:]
            file_path.write_text("\n".join(new_lines), encoding="utf-8")
            return True
        
        # Otherwise, add at the very beginning
        else:
            new_content = MASTER_REF + content
            file_path.write_text(new_content, encoding="utf-8")
            return True
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def find_all_diagrams() -> List[Path]:
    """Find all .mmd files in agent-orchestrator"""
    diagrams = []
    for mmd_file in BASE_DIR.rglob("*.mmd"):
        # Skip if in .git or __pycache__
        if ".git" in str(mmd_file) or "__pycache__" in str(mmd_file):
            continue
        diagrams.append(mmd_file)
    return diagrams

if __name__ == "__main__":
    diagrams = find_all_diagrams()
    updated = 0
    skipped = 0
    
    print(f"Found {len(diagrams)} diagram files")
    print("=" * 60)
    
    for diagram_path in diagrams:
        rel_path = diagram_path.relative_to(BASE_DIR)
        if add_reference_to_file(diagram_path):
            print(f"Updated: {rel_path}")
            updated += 1
        else:
            print(f"Skipped (already has reference): {rel_path}")
            skipped += 1
    
    print("=" * 60)
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")
    print(f"Total: {len(diagrams)}")
