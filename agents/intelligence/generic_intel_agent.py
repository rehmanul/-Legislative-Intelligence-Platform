
"""
Intelligence Agent: Generic Document Analysis
Class: Intelligence (Read-Only)
Purpose: Analyze uploaded documents for key insights, risks, and entities.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from agents.base.agent_base import AgentBase

class GenericIntelligenceAgent(AgentBase):
    """
    Generic intelligence agent for analyzing uploaded documents.
    """
    
    AGENT_ID = "intel_doc_analysis"
    RESPONSIBILITY = "Analyze uploaded documents for key insights"
    
    def __init__(self, workflow_id: str, artifact_path: str):
        super().__init__(workflow_id)
        self.artifact_path = Path(artifact_path)
        # Unique ID for this specific run
        self.AGENT_ID = f"intel_doc_analysis_{workflow_id}"
        
    def execute(self) -> Dict[str, Any]:
        """Execute document analysis logic"""
        
        # 1. Read document content
        content = ""
        try:
            if self.artifact_path.suffix.lower() == ".json":
                data = json.loads(self.artifact_path.read_text(encoding="utf-8"))
                content = json.dumps(data, indent=2)
            else:
                # Assuming text content was already extracted or plain text
                # In main.py we extract PDF text to .meta.json or similar, 
                # but here let's assume raw text reading for MVP
                content = self.artifact_path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            content = f"Error reading file: {e}"
            
        # 2. Perform Analysis (Heuristic / MVP Logic)
        # In a full production system with LLMs, this would call OpenAI/Anthropic
        
        analysis = {
            "document_type": self._detect_document_type(content),
            "key_entities": self._extract_entities(content),
            "risk_assessment": self._assess_risk(content),
            "summary": self._generate_summary(content),
            "analysis_metadata": {
                "analyzer": "GenericIntelligenceAgent v1.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "content_length": len(content)
            }
        }
        
        return analysis
    
    def _detect_document_type(self, content: str) -> str:
        content_lower = content.lower()
        if "policy" in content_lower or "regulation" in content_lower:
            return "Policy Document"
        elif "meeting" in content_lower or "agenda" in content_lower:
            return "Meeting Minutes"
        elif "budget" in content_lower or "cost" in content_lower:
            return "Financial Document"
        else:
            return "General Artifact"
            
    def _extract_entities(self, content: str) -> list:
        # Simple heuristic entity extraction
        entities = []
        words = content.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 1:
                # Very basic proper noun detection
                entities.append(word.strip(".,;:()"))
        return list(set(entities))[:10]  # Return top 10 unique
    
    def _assess_risk(self, content: str) -> str:
        risk_keywords = ["danger", "critical", "risk", "failure", "violation", "compliance"]
        count = sum(1 for word in risk_keywords if word in content.lower())
        if count > 5:
            return "HIGH"
        elif count > 2:
            return "MEDIUM"
        else:
            return "LOW"
            
    def _generate_summary(self, content: str) -> str:
        # First 200 character preview
        return content[:200] + "..." if len(content) > 200 else content

    def _is_stop_condition_met(self, output_value: Any) -> bool:
        return True
