#!/usr/bin/env python3
"""
Wi-Charge Technology Policy Scenario Analysis
Analyzes bill S.2296 in context of wireless power technology and air quality monitoring
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add codebase paths
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR.parent / "investment-sales-bd"))
sys.path.insert(0, str(BASE_DIR.parent / "risk-management-system"))

# Try to import PDF parser
try:
    from agents.parsing.pdf_parser import PDFParser
    PDF_PARSER_AVAILABLE = True
except ImportError:
    PDF_PARSER_AVAILABLE = False
    print("[WARNING] PDF parser not available - will use basic extraction")

# Document paths
BILL_PATH = Path(r"C:\Users\phi3t\OneDrive\Desktop\wu-tran clan\2025 wi charge\.2025 government capture\BILLS-119s2296es.pdf")
OUTPUT_DIR = BASE_DIR / "artifacts" / "wi_charge_scenario"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_bill_content(pdf_path: Path) -> Dict[str, Any]:
    """Extract FULL content from bill PDF - ALL PAGES"""
    if not pdf_path.exists():
        return {
            "error": f"Bill PDF not found at {pdf_path}",
            "extracted": False
        }
    
    # Try direct extraction first (faster)
    try:
        import pdfplumber
        print(f"  [INFO] Using pdfplumber for full extraction...")
        text_parts = []
        page_texts = []
        
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"  [INFO] Processing {total_pages} pages...")
            
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    text_parts.append(text)
                    page_texts.append({
                        "page": page_num,
                        "text": text,
                        "char_count": len(text)
                    })
                if page_num % 50 == 0:
                    print(f"  [PROGRESS] Extracted {page_num}/{total_pages} pages...")
        
        full_text = "\n\n".join(text_parts)
        print(f"  [SUCCESS] Extracted {len(page_texts)} pages, {len(full_text):,} characters")
        
        return {
            "extracted": True,
            "full_text": full_text,
            "pages": page_texts,
            "page_count": len(page_texts),
            "total_chars": len(full_text),
            "method": "pdfplumber"
        }
    except ImportError:
        pass  # Try PyMuPDF
    except Exception as e:
        print(f"  [WARNING] pdfplumber failed: {e}, trying fallback...")
    
    # Try PyMuPDF fallback
    try:
        import fitz  # PyMuPDF
        print(f"  [INFO] Using PyMuPDF for full extraction...")
        doc = fitz.open(pdf_path)
        text_parts = []
        page_texts = []
        total_pages = len(doc)
        print(f"  [INFO] Processing {total_pages} pages...")
        
        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text()
            if text:
                text_parts.append(text)
                page_texts.append({
                    "page": page_num + 1,
                    "text": text,
                    "char_count": len(text)
                })
            if (page_num + 1) % 50 == 0:
                print(f"  [PROGRESS] Extracted {page_num + 1}/{total_pages} pages...")
        
        doc.close()
        full_text = "\n\n".join(text_parts)
        print(f"  [SUCCESS] Extracted {len(page_texts)} pages, {len(full_text):,} characters")
        
        return {
            "extracted": True,
            "full_text": full_text,
            "pages": page_texts,
            "page_count": len(page_texts),
            "total_chars": len(full_text),
            "method": "PyMuPDF"
        }
    except ImportError:
        pass
    except Exception as e:
        print(f"  [WARNING] PyMuPDF failed: {e}, trying basic extraction...")
    
    # Last resort: PyPDF2 (may be limited)
    try:
        import PyPDF2
        print(f"  [INFO] Using PyPDF2 for extraction (may be limited)...")
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text_parts = []
            page_texts = []
            total_pages = len(pdf_reader.pages)
            print(f"  [INFO] Processing {total_pages} pages...")
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text:
                    text_parts.append(text)
                    page_texts.append({
                        "page": page_num,
                        "text": text,
                        "char_count": len(text)
                    })
                if page_num % 50 == 0:
                    print(f"  [PROGRESS] Extracted {page_num}/{total_pages} pages...")
            
            full_text = "\n\n".join(text_parts)
            print(f"  [SUCCESS] Extracted {len(page_texts)} pages, {len(full_text):,} characters")
            
            return {
                "extracted": True,
                "full_text": full_text,
                "pages": page_texts,
                "page_count": len(page_texts),
                "total_chars": len(full_text),
                "method": "PyPDF2"
            }
    except Exception as e:
        return {
            "error": f"All PDF extraction methods failed. Last error: {e}",
            "extracted": False,
            "suggestion": "Install pdfplumber: pip install pdfplumber"
        }
    
    return {"extracted": False, "error": "No PDF extraction libraries available"}

def analyze_bill_content(bill_content: str, tech_context: Dict[str, Any]) -> Dict[str, Any]:
    """DEEP analysis of bill content in context of technology"""
    
    analysis = {
        "bill_number": "S.2296",
        "analysis_date": datetime.utcnow().isoformat(),
        "technology_context": tech_context,
        "key_findings": [],
        "policy_opportunities": [],
        "technology_alignment": {},
        "uncertainty_notes": [],
        "section_analysis": {},
        "funding_mentions": [],
        "technology_provisions": []
    }
    
    bill_lower = bill_content.lower()
    bill_lines = bill_content.split('\n')
    
    # Enhanced keyword search with context
    tech_keywords = {
        "wireless": ["wireless", "wireless power", "wireless charging", "wireless technology"],
        "energy": ["energy", "energy efficiency", "power", "electricity", "energy infrastructure", "energy cost savings"],
        "iot": ["iot", "internet of things", "smart devices", "connected devices", "sensors", "sensor networks"],
        "air_quality": ["air quality", "indoor air", "ventilation", "hvac", "air monitoring", "airborne"],
        "building": ["building", "buildings", "infrastructure", "construction", "facility", "facilities", "military construction"],
        "standards": ["standards", "regulations", "compliance", "certification", "guidelines"],
        "research": ["research", "development", "rd&e", "r&d", "darpa", "advanced research"],
        "manufacturing": ["manufacturing", "advanced manufacturing", "additive manufacturing", "production"],
        "technology": ["technology", "technologies", "tech", "innovation", "advanced"]
    }
    
    keyword_matches = {}
    keyword_contexts = {}  # Store context around matches
    
    for category, keywords in tech_keywords.items():
        matches = []
        contexts = []
        for keyword in keywords:
            if keyword in bill_lower:
                matches.append(keyword)
                # Find context around matches
                idx = bill_lower.find(keyword)
                if idx != -1:
                    start = max(0, idx - 200)
                    end = min(len(bill_content), idx + len(keyword) + 200)
                    context = bill_content[start:end].replace('\n', ' ').strip()
                    contexts.append({
                        "keyword": keyword,
                        "context": context[:300]  # Limit context length
                    })
        if matches:
            keyword_matches[category] = matches
            keyword_contexts[category] = contexts[:5]  # Top 5 contexts per category
    
    analysis["keyword_matches"] = keyword_matches
    analysis["keyword_contexts"] = keyword_contexts
    
    # Extract bill structure
    divisions = []
    titles = []
    sections = []
    subtitles = []
    
    for i, line in enumerate(bill_lines):
        line_upper = line.upper().strip()
        
        # Divisions
        if "DIVISION" in line_upper and ("—" in line or "-" in line):
            divisions.append({"line": i+1, "text": line.strip()[:150]})
        
        # Titles
        if "TITLE" in line_upper and ("—" in line or "-" in line) and "TABLE" not in line_upper:
            titles.append({"line": i+1, "text": line.strip()[:150]})
        
        # Sections
        if ("SEC." in line_upper or "SECTION" in line_upper) and any(char.isdigit() for char in line):
            sections.append({"line": i+1, "text": line.strip()[:200]})
        
        # Subtitles
        if "SUBTITLE" in line_upper and ("—" in line or "-" in line):
            subtitles.append({"line": i+1, "text": line.strip()[:150]})
    
    analysis["bill_structure"] = {
        "divisions": divisions[:20],  # Top 20
        "titles": titles[:30],
        "sections": sections[:100],  # Top 100 sections
        "subtitles": subtitles[:30]
    }
    
    # Find specific relevant sections
    relevant_sections = []
    for section in sections:
        section_text = section["text"].lower()
        if any(kw in section_text for kw in ["energy", "research", "development", "technology", "infrastructure", 
                                              "construction", "building", "manufacturing", "iot", "sensor"]):
            relevant_sections.append(section)
    
    analysis["relevant_sections"] = relevant_sections[:50]
    
    # Extract funding mentions
    funding_patterns = [
        r'\$[\d,]+(?:\.\d+)?\s*(?:million|billion|thousand)?',
        r'authorization of appropriations',
        r'authorized to be appropriated',
        r'funding',
        r'appropriation'
    ]
    
    import re
    funding_mentions = []
    for pattern in funding_patterns:
        matches = re.finditer(pattern, bill_lower, re.IGNORECASE)
        for match in matches:
            start = max(0, match.start() - 100)
            end = min(len(bill_content), match.end() + 100)
            context = bill_content[start:end].replace('\n', ' ').strip()
            funding_mentions.append({
                "pattern": pattern,
                "match": match.group(),
                "context": context[:250]
            })
    
    analysis["funding_mentions"] = funding_mentions[:30]  # Top 30
    
    # Technology-specific provision extraction
    tech_provisions = []
    for i, line in enumerate(bill_lines):
        line_lower = line.lower()
        if any(tech_term in line_lower for tech_term in ["wireless", "sensor", "iot", "smart", "connected", 
                                                          "energy efficiency", "air quality", "hvac"]):
            # Get surrounding context
            start = max(0, i - 5)
            end = min(len(bill_lines), i + 10)
            context = "\n".join(bill_lines[start:end])
            tech_provisions.append({
                "line": i+1,
                "text": line.strip()[:200],
                "context": context[:500]
            })
    
    analysis["technology_provisions"] = tech_provisions[:40]  # Top 40
    
    # Extract bill title
    for i, line in enumerate(bill_lines[:50]):
        if "S.2296" in line or ("NATIONAL DEFENSE" in line.upper() and "AUTHORIZATION" in line.upper()):
            analysis["bill_title"] = line.strip()
            break
    
    return analysis

def generate_section_analysis(bill_analysis: Dict[str, Any], bill_content: str) -> Dict[str, Any]:
    """Generate detailed analysis of relevant bill sections"""
    
    analysis = {
        "divisions": {},
        "key_sections": [],
        "funding_analysis": {},
        "technology_opportunities": []
    }
    
    # Analyze divisions
    structure = bill_analysis.get("bill_structure", {})
    divisions = structure.get("divisions", [])
    
    for div in divisions[:10]:  # Top 10 divisions
        div_text = div["text"].lower()
        if any(kw in div_text for kw in ["energy", "construction", "research", "technology", "defense"]):
            analysis["divisions"][div["text"][:100]] = {
                "line": div["line"],
                "relevance": "high" if any(kw in div_text for kw in ["energy", "construction"]) else "medium"
            }
    
    # Extract key sections with full context
    relevant_sections = bill_analysis.get("relevant_sections", [])
    for section in relevant_sections[:20]:  # Top 20
        analysis["key_sections"].append({
            "section_text": section["text"],
            "line": section["line"],
            "relevance_score": len([kw for kw in ["energy", "research", "technology", "infrastructure"] 
                                   if kw in section["text"].lower()])
        })
    
    # Funding analysis
    funding_mentions = bill_analysis.get("funding_mentions", [])
    if funding_mentions:
        analysis["funding_analysis"] = {
            "total_mentions": len(funding_mentions),
            "sample_mentions": funding_mentions[:5]
        }
    
    # Technology opportunities
    tech_provisions = bill_analysis.get("technology_provisions", [])
    for prov in tech_provisions[:15]:  # Top 15
        analysis["technology_opportunities"].append({
            "provision": prov["text"],
            "context": prov["context"][:300],
            "line": prov["line"]
        })
    
    return analysis

def create_scenario_analysis(bill_analysis: Dict[str, Any], tech_specs: Dict[str, Any]) -> Dict[str, Any]:
    """Create comprehensive scenario analysis"""
    
    scenario = {
        "_meta": {
            "scenario_id": "wi_charge_air_quality_policy",
            "generated_at": datetime.utcnow().isoformat(),
            "bill_number": "S.2296",
            "analysis_type": "Technology-Policy Alignment Assessment"
        },
        "bill_analysis": bill_analysis,
        "technology_specifications": tech_specs,
        "policy_technology_alignment": {},
        "opportunity_assessment": {},
        "recommendations": []
    }
    
    # Technology specs from documents
    scenario["technology_specifications"] = {
        "wireless_power": {
            "device": "Wi-Charge R1/R1HP Transmitter",
            "power_delivery": "100mW at 10m (R1) or 300mW at 5m (R1HP)",
            "applications": ["IoT devices", "Security systems", "Digital signage", "Medical devices"],
            "connectivity": "Wi-Fi enabled",
            "safety": "Class 1 laser product, US and international compliance"
        },
        "air_quality_monitoring": {
            "power_requirements": "USB-C or PoE",
            "connectivity": "Wi-Fi or cellular (2.4GHz/5GHz)",
            "storage": "12+ hours local storage",
            "integration": "Building management systems (HVAC control)",
            "software": "Dashboard, mobile apps, API access, alerts, data export",
            "standards": "LEED and WELL building standards compliance"
        }
    }
    
    # Alignment analysis
    keyword_matches = bill_analysis.get("keyword_matches", {})
    alignment_score = len(keyword_matches) / len(tech_specs.keys()) if tech_specs else 0
    
    scenario["policy_technology_alignment"] = {
        "alignment_score": alignment_score,
        "matched_categories": list(keyword_matches.keys()),
        "alignment_strength": "high" if alignment_score > 0.5 else "medium" if alignment_score > 0.2 else "low",
        "key_connections": []
    }
    
    # Opportunity assessment
    scenario["opportunity_assessment"] = {
        "policy_window": "unknown",
        "technology_relevance": "high" if keyword_matches else "unknown",
        "stakeholder_implications": "to_be_analyzed",
        "regulatory_considerations": "to_be_analyzed"
    }
    
    return scenario

def main():
    """Main analysis function"""
    print("=" * 80)
    print("Wi-Charge Technology Policy Scenario Analysis")
    print("=" * 80)
    print(f"\nBill: S.2296")
    print(f"Bill Path: {BILL_PATH}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print("-" * 80)
    
    # Step 1: Extract FULL bill content
    print("\n[1/5] Extracting FULL bill content (ALL PAGES)...")
    print("=" * 80)
    bill_content_result = extract_bill_content(BILL_PATH)
    
    if not bill_content_result.get("extracted"):
        print(f"\n[ERROR] Failed to extract bill content: {bill_content_result.get('error', 'Unknown error')}")
        print("\n[INFO] Creating scenario framework without bill content...")
        bill_content = ""
    else:
        bill_content = bill_content_result.get("full_text", "")
        method = bill_content_result.get("method", "unknown")
        print(f"\n[SUCCESS] Full extraction complete!")
        print(f"  Method: {method}")
        print(f"  Pages: {bill_content_result.get('page_count', 'unknown')}")
        print(f"  Characters: {bill_content_result.get('total_chars', len(bill_content)):,}")
        print(f"  Words: ~{len(bill_content.split()):,}")
    
    # Step 2: DEEP analysis of bill content
    print("\n[2/5] Performing DEEP analysis of bill content...")
    print("=" * 80)
    tech_context = {
        "wireless_power": "Wi-Charge R1 transmitter technology",
        "air_quality": "Building air quality monitoring requirements",
        "iot_devices": "Connected device ecosystem"
    }
    
    bill_analysis = analyze_bill_content(bill_content, tech_context)
    print(f"[SUCCESS] Deep analysis complete")
    print(f"  Keyword categories matched: {len(bill_analysis.get('keyword_matches', {}))}")
    print(f"  Relevant sections identified: {len(bill_analysis.get('relevant_sections', []))}")
    print(f"  Technology provisions found: {len(bill_analysis.get('technology_provisions', []))}")
    print(f"  Funding mentions: {len(bill_analysis.get('funding_mentions', []))}")
    
    # Step 3: Create comprehensive scenario analysis
    print("\n[3/5] Creating comprehensive scenario analysis...")
    tech_specs = {
        "wireless_power": True,
        "air_quality": True,
        "iot": True,
        "energy": True,
        "building": True,
        "standards": True
    }
    
    scenario = create_scenario_analysis(bill_analysis, tech_specs)
    print(f"[SUCCESS] Scenario analysis created")
    
    # Step 4: Generate detailed section analysis
    print("\n[4/5] Generating detailed section analysis...")
    section_analysis = generate_section_analysis(bill_analysis, bill_content)
    scenario["detailed_section_analysis"] = section_analysis
    print(f"[SUCCESS] Section analysis complete")
    print(f"  Divisions analyzed: {len(section_analysis.get('divisions', {}))}")
    print(f"  Key sections extracted: {len(section_analysis.get('key_sections', []))}")
    
    # Step 5: Save all artifacts
    print("\n[5/5] Saving all artifacts...")
    print("=" * 80)
    
    # Save markdown summary
    markdown_file = OUTPUT_DIR / "SCENARIO_ANALYSIS.md"
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write(f"# Wi-Charge Technology Policy Scenario Analysis\n\n")
        f.write(f"**Bill:** S.2296\n")
        f.write(f"**Analysis Date:** {datetime.utcnow().isoformat()}\n")
        f.write(f"**Status:** {'Bill Content Extracted' if bill_content_result.get('extracted') else 'Framework Only (Bill Extraction Failed)'}\n\n")
        f.write(f"## Bill Analysis Summary\n\n")
        f.write(f"- **Content Extracted:** {bill_content_result.get('extracted', False)}\n")
        f.write(f"- **Character Count:** {bill_content_result.get('total_chars', len(bill_content)):,}\n")
        f.write(f"- **Pages:** {bill_content_result.get('page_count', 'unknown')}\n\n")
        f.write(f"## Keyword Matches\n\n")
        for category, matches in bill_analysis.get('keyword_matches', {}).items():
            f.write(f"- **{category.replace('_', ' ').title()}:** {', '.join(matches)}\n")
        f.write(f"\n## Technology Context\n\n")
        f.write(f"### Wireless Power (Wi-Charge R1)\n")
        f.write(f"- Power Delivery: 100mW at 10m (R1) or 300mW at 5m (R1HP)\n")
        f.write(f"- Applications: IoT devices, security systems, digital signage, medical devices\n")
        f.write(f"- Connectivity: Wi-Fi enabled\n\n")
        f.write(f"### Air Quality Monitoring\n")
        f.write(f"- Power: USB-C or PoE\n")
        f.write(f"- Connectivity: Wi-Fi or cellular\n")
        f.write(f"- Integration: Building management systems (HVAC)\n")
        f.write(f"- Standards: LEED and WELL compliance\n\n")
        f.write(f"## Policy-Technology Alignment\n\n")
        f.write(f"- **Alignment Score:** {scenario['policy_technology_alignment']['alignment_score']:.2%}\n")
        f.write(f"- **Alignment Strength:** {scenario['policy_technology_alignment']['alignment_strength'].upper()}\n")
        f.write(f"- **Matched Categories:** {', '.join(scenario['policy_technology_alignment']['matched_categories'])}\n\n")
        f.write(f"## Next Steps\n\n")
        f.write(f"1. Full bill text analysis (if extraction successful)\n")
        f.write(f"2. Section-by-section policy analysis\n")
        f.write(f"3. Technology-policy opportunity mapping\n")
        f.write(f"4. Stakeholder impact assessment\n")
        f.write(f"5. Regulatory pathway identification\n")
    
    print(f"[SUCCESS] Markdown summary saved: {markdown_file}")
    
    # Save JSON artifact
    json_file = OUTPUT_DIR / "scenario_analysis.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(scenario, f, indent=2, ensure_ascii=False)
    print(f"[SUCCESS] JSON artifact saved: {json_file}")
    
    # Save FULL bill content (if extracted)
    if bill_content_result.get("extracted") and bill_content:
        bill_text_file = OUTPUT_DIR / "bill_content_FULL.txt"
        with open(bill_text_file, 'w', encoding='utf-8') as f:
            f.write(bill_content)  # FULL content
        print(f"[SUCCESS] FULL bill content saved: {bill_text_file}")
        print(f"  Size: {len(bill_content):,} characters")
        
        # Also save per-page extracts
        pages_dir = OUTPUT_DIR / "pages"
        pages_dir.mkdir(exist_ok=True)
        pages = bill_content_result.get("pages", [])
        for page_data in pages[:10]:  # Save first 10 pages as samples
            page_file = pages_dir / f"page_{page_data['page']:04d}.txt"
            with open(page_file, 'w', encoding='utf-8') as f:
                f.write(page_data.get("text", ""))
        print(f"[SUCCESS] Sample pages saved to: {pages_dir}")
    
    # Save detailed analysis JSON
    detailed_analysis_file = OUTPUT_DIR / "detailed_analysis.json"
    with open(detailed_analysis_file, 'w', encoding='utf-8') as f:
        json.dump({
            "bill_analysis": bill_analysis,
            "scenario": scenario,
            "section_analysis": section_analysis,
            "extraction_metadata": {
                "method": bill_content_result.get("method"),
                "page_count": bill_content_result.get("page_count"),
                "total_chars": bill_content_result.get("total_chars")
            }
        }, f, indent=2, ensure_ascii=False)
    print(f"[SUCCESS] Detailed analysis JSON saved: {detailed_analysis_file}")
    
    print("\n" + "=" * 80)
    print("Analysis Complete!")
    print("=" * 80)
    print(f"\nArtifacts saved to: {OUTPUT_DIR}")
    print(f"\nNext: Review SCENARIO_ANALYSIS.md for summary")
    
    return scenario

if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
