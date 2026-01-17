# Bill Risk Capability Matching Agent

## Overview

The `intel_bill_risk_capability_match_pre_evt` agent analyzes legislative bills to extract risk-management signals and assess alignment with wireless, low-power sensing capabilities.

## Purpose

- Extract risk-relevant language from bill text
- Identify risk domains (environmental, safety, operational, etc.)
- Map statutory requirements to abstract capability classes
- Assess alignment with wireless sensing capabilities
- Analyze temporal/political context (2026 midterm elections)

## Usage

### Basic Usage

```bash
# Analyze a bill file
python agents/intel_risk/intel_bill_risk_capability_match_pre_evt.py path/to/bill.pdf

# With metadata JSON
python agents/intel_risk/intel_bill_risk_capability_match_pre_evt.py path/to/bill.pdf path/to/metadata.json
```

### Bill Metadata Format

Create a JSON file with bill metadata (optional but recommended):

```json
{
  "bill_id": "S.1071",
  "bill_number": "S.1071",
  "congress": 119,
  "title": "National Defense Authorization Act for Fiscal Year 2026",
  "status": "enacted",
  "enactment_date": "2025-12-18",
  "fiscal_year": 2026,
  "signed_by": "President Trump"
}
```

### Supported File Formats

- PDF (`.pdf`) - Requires `pdfplumber` or `PyMuPDF`
- HTML (`.html`, `.htm`) - Requires `beautifulsoup4`
- Plain text (`.txt`, `.md`)

## Output

The agent generates a JSON artifact in `artifacts/intel_risk/` with:

- **Risk relevance**: direct, indirect, latent, or none
- **Risk domains**: List of identified domains
- **Statutory signals**: Extracted risk signals with sections and text excerpts
- **Capability requirements**: Abstract capability classes (no vendor/product names)
- **Wireless risk alignment**: Alignment level and justification
- **Temporal context**: Election-year timing, bill status, implementation timelines

## Example Output

```json
{
  "_meta": {
    "agent_id": "intel_bill_risk_capability_match_pre_evt",
    "generated_at": "2026-01-20T12:00:00Z",
    "artifact_type": "BILL_RISK_ANALYSIS",
    "status": "SPECULATIVE",
    "confidence": "MEDIUM"
  },
  "bill_id": "H.R.1234",
  "risk_relevance": "direct",
  "risk_domains": ["environmental", "safety"],
  "statutory_signals": [
    {
      "section": "Sec. 5",
      "signal_type": "monitoring",
      "text_excerpt": "The Administrator shall monitor...",
      "risk_domain": "environmental"
    }
  ],
  "capability_requirements": [
    "continuous_monitoring",
    "distributed_sensing",
    "low_power_operation"
  ],
  "wireless_risk_alignment": {
    "alignment_level": "high",
    "justification": "Bill requires continuous environmental monitoring..."
  },
  "temporal_context": {
    "bill_status": "pending",
    "election_year": true,
    "days_until_election": 287,
    "timing_urgency": "high"
  }
}
```

## Dependencies

Install required dependencies:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `sentence-transformers` - Semantic similarity for risk domain classification
- `pdfplumber` or `PyMuPDF` - PDF parsing
- `beautifulsoup4` - HTML parsing

## Testing

Run unit tests:

```bash
pytest tests/test_bill_risk_analyzer.py
```

## Notes

- Agent is read-only (Intelligence agent, no review required)
- Outputs are SPECULATIVE by default
- Never names vendors/products - only abstract capability classes
- Uses institutional language (not marketing)
- Handles pending, enacted, and historical bills
