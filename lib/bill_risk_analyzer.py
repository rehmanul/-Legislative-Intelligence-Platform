"""
Bill Risk Capability Analyzer
Core analysis library for extracting risk-management signals from legislative bills
and assessing alignment with wireless, low-power sensing capabilities.
"""

import json
import re
from datetime import datetime, date, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    try:
        import fitz  # PyMuPDF
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    HTML_AVAILABLE = True
except ImportError:
    HTML_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False


class RiskDomain(Enum):
    """Risk domain classifications"""
    ENVIRONMENTAL = "environmental"
    SAFETY = "safety"
    OPERATIONAL = "operational"
    INFRASTRUCTURE = "infrastructure"
    HEALTH = "health"
    CYBER = "cyber"
    FINANCIAL = "financial"
    COMPLIANCE = "compliance"


class BillStatus(Enum):
    """Bill status categories"""
    PENDING = "pending"
    ENACTED = "enacted"
    HISTORICAL = "historical"


class BillParser:
    """Parse bills from various formats (PDF, HTML, text)"""
    
    def __init__(self):
        self.supported_formats = []
        if PDF_AVAILABLE:
            self.supported_formats.append("pdf")
        if HTML_AVAILABLE:
            self.supported_formats.append("html")
        self.supported_formats.append("txt")
        self.supported_formats.append("md")
    
    def parse(self, file_path: Path, file_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse a bill file and extract text content
        
        Args:
            file_path: Path to bill file
            file_type: Optional file type hint (pdf, html, txt, md)
            
        Returns:
            Dict with 'text', 'file_type', 'file_path', 'parsed_at'
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Bill file not found: {file_path}")
        
        if file_type is None:
            file_type = self._detect_file_type(file_path)
        
        if file_type == "pdf":
            text = self._extract_text_pdf(file_path)
        elif file_type == "html":
            text = self._extract_text_html(file_path)
        else:
            text = self._extract_text_plain(file_path)
        
        return {
            "text": text,
            "file_type": file_type,
            "file_path": str(file_path),
            "parsed_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
    
    def _detect_file_type(self, file_path: Path) -> str:
        """Detect file type from extension"""
        ext = file_path.suffix.lower()
        if ext == ".pdf":
            return "pdf"
        elif ext in [".html", ".htm"]:
            return "html"
        elif ext in [".txt", ".md"]:
            return ext[1:]  # Remove dot
        else:
            return "txt"  # Default
    
    def _extract_text_pdf(self, file_path: Path) -> str:
        """Extract text from PDF"""
        if not PDF_AVAILABLE:
            raise ImportError("PDF parsing requires pdfplumber or PyMuPDF")
        
        try:
            # Try pdfplumber first
            import pdfplumber
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text_parts.append(page.extract_text() or "")
            return "\n\n".join(text_parts)
        except ImportError:
            # Fallback to PyMuPDF
            import fitz
            doc = fitz.open(file_path)
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()
            return "\n\n".join(text_parts)
    
    def _extract_text_html(self, file_path: Path) -> str:
        """Extract text from HTML"""
        if not HTML_AVAILABLE:
            raise ImportError("HTML parsing requires beautifulsoup4")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        return soup.get_text(separator='\n', strip=True)
    
    def _extract_text_plain(self, file_path: Path) -> str:
        """Extract text from plain text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()


class BillStructureExtractor:
    """Extract structural elements from bill text"""
    
    def __init__(self):
        # Enhanced patterns for bill structure - handle NDAA formats better
        # Pattern matches: SEC. 7401, Section 244, §2829, SEC. 2829/2830, etc.
        self.section_pattern = re.compile(
            r'(?:^|\n)\s*(?:SEC\.|Section|§)\s*(\d+(?:[A-Z]?|/\d+)?)[\.:]?\s*(.+?)(?=\n\s*(?:SEC\.|Section|§|\d+(?:[A-Z]?|/\d+)?[\.:]|$))',
            re.MULTILINE | re.IGNORECASE | re.DOTALL
        )
        self.definition_pattern = re.compile(r'(?:^|\n)\s*\((\d+)\)\s*["\']?([^"\']+?)["\']?\s*[\.:]', re.MULTILINE)
        self.requirement_verbs = ["shall", "must", "required", "mandate", "direct"]
        self.authorization_verbs = ["authorize", "authorized", "appropriation", "appropriate"]
        self.report_verbs = ["report", "submit", "notify", "inform"]
    
    def extract_structure(self, text: str) -> Dict[str, Any]:
        """
        Extract structural elements from bill text
        
        Returns:
            Dict with 'sections', 'definitions', 'requirements', 'authorizations', 'reports'
        """
        sections = self._extract_sections(text)
        definitions = self._extract_definitions(text)
        requirements = self._extract_requirements(text)
        authorizations = self._extract_authorizations(text)
        reports = self._extract_reports(text)
        
        return {
            "sections": sections,
            "definitions": definitions,
            "requirements": requirements,
            "authorizations": authorizations,
            "reports": reports
        }
    
    def _extract_sections(self, text: str) -> List[Dict[str, Any]]:
        """Extract bill sections with position tracking"""
        sections = []
        lines = text.split('\n')
        
        for match in self.section_pattern.finditer(text):
            section_number = match.group(1)
            title = match.group(2).strip()[:200]  # Limit title length
            start_pos = match.start()
            end_pos = match.end()
            
            # Calculate line numbers for this section
            lines_before = text[:start_pos].count('\n')
            section_text = match.group(0)
            
            # Extract full section text (until next section or end)
            next_match_start = len(text)
            for next_match in self.section_pattern.finditer(text, end_pos):
                next_match_start = next_match.start()
                break
            
            full_section_text = text[start_pos:next_match_start].strip()
            
            sections.append({
                "section_number": section_number,
                "title": title,
                "text_excerpt": section_text[:500],  # First 500 chars of header
                "full_text": full_section_text[:2000],  # Full section text (limited)
                "start_char": start_pos,
                "end_char": next_match_start,
                "start_line": lines_before + 1,
                "end_line": text[:next_match_start].count('\n') + 1
            })
        
        return sections
    
    def _extract_definitions(self, text: str) -> List[Dict[str, Any]]:
        """Extract definition sections"""
        definitions = []
        for match in self.definition_pattern.finditer(text):
            definitions.append({
                "number": match.group(1),
                "term": match.group(2).strip()
            })
        return definitions
    
    def _extract_requirements(self, text: str) -> List[Dict[str, Any]]:
        """Extract requirement statements with context"""
        requirements = []
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(verb in line_lower for verb in self.requirement_verbs):
                # Include context (previous and next line if available)
                context_lines = []
                if i > 0:
                    context_lines.append(lines[i-1].strip())
                context_lines.append(line.strip())
                if i < len(lines) - 1:
                    context_lines.append(lines[i+1].strip())
                
                requirements.append({
                    "line_number": i + 1,
                    "text": line.strip(),
                    "context": " ".join(context_lines),
                    "verb": next((v for v in self.requirement_verbs if v in line_lower), None),
                    "char_position": sum(len(l) + 1 for l in lines[:i])  # Approximate char position
                })
        return requirements
    
    def _extract_authorizations(self, text: str) -> List[Dict[str, Any]]:
        """Extract authorization statements"""
        authorizations = []
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(verb in line_lower for verb in self.authorization_verbs):
                authorizations.append({
                    "line_number": i + 1,
                    "text": line.strip(),
                    "verb": next((v for v in self.authorization_verbs if v in line_lower), None)
                })
        return authorizations
    
    def _extract_reports(self, text: str) -> List[Dict[str, Any]]:
        """Extract reporting requirements"""
        reports = []
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(verb in line_lower for verb in self.report_verbs):
                reports.append({
                    "line_number": i + 1,
                    "text": line.strip(),
                    "verb": next((v for v in self.report_verbs if v in line_lower), None)
                })
        return reports


class RiskLanguageExtractor:
    """Extract risk-relevant language using semantic similarity"""
    
    def __init__(self):
        self.risk_domain_keywords = {
            RiskDomain.ENVIRONMENTAL: [
                "environment", "emission", "pollution", "air quality", "water quality",
                "climate", "carbon", "greenhouse", "hazardous", "contamination"
            ],
            RiskDomain.SAFETY: [
                "safety", "hazard", "danger", "accident", "injury", "fatality",
                "worker safety", "public safety", "fire", "explosion"
            ],
            RiskDomain.OPERATIONAL: [
                "operational", "failure", "downtime", "reliability", "uptime",
                "system failure", "equipment failure", "outage", "disruption"
            ],
            RiskDomain.INFRASTRUCTURE: [
                "infrastructure", "critical infrastructure", "resilience", "condition",
                "degradation", "maintenance", "asset", "facility"
            ],
            RiskDomain.HEALTH: [
                "health", "disease", "exposure", "contamination", "public health",
                "epidemic", "pandemic", "medical", "healthcare"
            ],
            RiskDomain.CYBER: [
                "cyber", "cybersecurity", "network", "data breach", "hack",
                "malware", "vulnerability", "security", "encryption"
            ],
            RiskDomain.FINANCIAL: [
                "financial", "loss", "insurance", "liability", "damage",
                "cost", "expense", "revenue", "budget"
            ],
            RiskDomain.COMPLIANCE: [
                "compliance", "regulation", "regulatory", "violation", "enforcement",
                "audit", "inspection", "certification", "standard"
            ]
        }
        
        # Risk signal verbs
        self.risk_verbs = [
            "monitor", "detect", "identify", "assess", "track", "report",
            "prevent", "mitigate", "reduce", "minimize", "avoid", "alert",
            "warn", "notify", "measure", "evaluate", "analyze"
        ]
        
        # Initialize semantic model if available
        self.semantic_model = None
        if SEMANTIC_AVAILABLE:
            try:
                self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception:
                pass  # Fallback to keyword matching
    
    def extract_risk_signals(self, text: str, structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract risk-relevant signals from bill text
        
        Returns:
            List of risk signals with section, signal_type, text_excerpt, risk_domain
        """
        signals = []
        
        # Extract from requirements
        for req in structure.get("requirements", []):
            signal = self._analyze_requirement(req.get("context", req["text"]))
            if signal:
                char_pos = req.get("char_position")
                signal["section"] = self._find_section_for_line(
                    req["line_number"], 
                    structure, 
                    char_position=char_pos
                )
                signal["text_excerpt"] = req["text"][:300]
                signals.append(signal)
        
        # Extract from sections (use full_text if available for better analysis)
        for section in structure.get("sections", []):
            section_text = section.get("full_text", section.get("text_excerpt", ""))
            section_signals = self._analyze_section(section_text)
            for sig in section_signals:
                sig["section"] = section["section_number"]
                sig["section_title"] = section.get("title", "")
                # Use more context from full section text
                sig["text_excerpt"] = section_text[:300] if section_text else section.get("text_excerpt", "")[:300]
                signals.append(sig)
        
        return signals
    
    def _analyze_requirement(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyze a requirement statement for risk signals"""
        text_lower = text.lower()
        
        # Check for risk verbs
        signal_type = None
        for verb in self.risk_verbs:
            if verb in text_lower:
                if verb in ["monitor", "track", "measure"]:
                    signal_type = "monitoring"
                elif verb in ["detect", "identify", "alert", "warn"]:
                    signal_type = "detection"
                elif verb in ["report", "notify", "submit"]:
                    signal_type = "reporting"
                elif verb in ["prevent", "mitigate", "reduce", "minimize", "avoid"]:
                    signal_type = "mitigation"
                break
        
        if not signal_type:
            return None
        
        # Identify risk domain
        risk_domain = self._identify_risk_domain(text)
        
        return {
            "signal_type": signal_type,
            "risk_domain": risk_domain.value if risk_domain else None
        }
    
    def _analyze_section(self, text: str) -> List[Dict[str, Any]]:
        """Analyze a section for risk signals"""
        signals = []
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            signal = self._analyze_requirement(sentence)
            if signal:
                signals.append(signal)
        
        return signals
    
    def _identify_risk_domain(self, text: str) -> Optional[RiskDomain]:
        """Identify risk domain from text"""
        text_lower = text.lower()
        
        # Keyword matching
        domain_scores = {}
        for domain, keywords in self.risk_domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores.items(), key=lambda x: x[1])[0]
        
        # Semantic similarity if model available
        if self.semantic_model:
            try:
                # Create embeddings for text and domain keywords
                text_embedding = self.semantic_model.encode([text], convert_to_tensor=False)[0]
                
                # Create domain keyword embeddings
                domain_embeddings = {}
                for domain, keywords in self.risk_domain_keywords.items():
                    keyword_text = " ".join(keywords)
                    domain_embeddings[domain] = self.semantic_model.encode(
                        [keyword_text], 
                        convert_to_tensor=False
                    )[0]
                
                # Calculate cosine similarity
                try:
                    import numpy as np
                    best_domain = None
                    best_score = 0.0
                    for domain, domain_emb in domain_embeddings.items():
                        # Cosine similarity
                        similarity = np.dot(text_embedding, domain_emb) / (np.linalg.norm(text_embedding) * np.linalg.norm(domain_emb))
                        if similarity > best_score and similarity > 0.3:  # Threshold for relevance
                            best_score = similarity
                            best_domain = domain
                    
                    if best_domain:
                        return best_domain
                except ImportError:
                    # numpy not available, skip semantic matching
                    pass
            except Exception:
                # Fallback to keyword matching if semantic fails
                pass
        
        return None
    
    def _find_section_for_line(self, line_number: int, structure: Dict[str, Any], char_position: Optional[int] = None) -> str:
        """Find which section a line number or character position belongs to"""
        sections = structure.get("sections", [])
        if not sections:
            return "Unknown"
        
        # If we have character position, use that (more accurate)
        if char_position is not None:
            for section in sections:
                if section.get("start_char", 0) <= char_position < section.get("end_char", float('inf')):
                    return section.get("section_number", "Unknown")
        
        # Fallback to line number matching
        for section in sections:
            start_line = section.get("start_line", 0)
            end_line = section.get("end_line", float('inf'))
            if start_line <= line_number <= end_line:
                return section.get("section_number", "Unknown")
        
        # If no exact match, find closest section
        best_section = None
        min_distance = float('inf')
        for section in sections:
            start_line = section.get("start_line", 0)
            distance = abs(line_number - start_line)
            if distance < min_distance:
                min_distance = distance
                best_section = section
        
        return best_section.get("section_number", "Unknown") if best_section else "Unknown"


class CapabilityMapper:
    """Map statutory language to abstract capability requirements"""
    
    def __init__(self):
        self.capability_patterns = {
            "continuous_monitoring": [
                "continuous", "ongoing", "real-time", "24/7", "around the clock",
                "constant", "persistent", "uninterrupted"
            ],
            "early_warning_detection": [
                "early warning", "advance notice", "prior to", "before",
                "preventive", "proactive", "anticipate"
            ],
            "distributed_sensing": [
                "distributed", "multiple locations", "network", "across",
                "various sites", "geographically dispersed"
            ],
            "condition_monitoring": [
                "condition", "health", "status", "state", "degradation",
                "wear", "deterioration", "performance"
            ],
            "anomaly_detection": [
                "anomaly", "unusual", "abnormal", "deviation", "irregular",
                "outlier", "exception"
            ],
            "uptime_assurance": [
                "uptime", "availability", "reliability", "operational",
                "functioning", "service", "downtime"
            ],
            "non_invasive_measurement": [
                "non-invasive", "non-intrusive", "without disruption",
                "remote", "external", "surface"
            ],
            "low_maintenance_operation": [
                "low maintenance", "minimal maintenance", "self-maintaining",
                "maintenance-free", "automated", "unattended"
            ],
            "wireless_communication": [
                "wireless", "remote", "telemetry", "data transmission",
                "communication", "connectivity"
            ],
            "low_power_operation": [
                "low power", "energy efficient", "battery", "solar",
                "power consumption", "energy"
            ]
        }
    
    def map_capabilities(self, text: str, risk_signals: List[Dict[str, Any]]) -> List[str]:
        """
        Map bill language to capability requirements
        
        Returns:
            List of capability requirement strings
        """
        capabilities = set()
        text_lower = text.lower()
        
        # Check each capability pattern
        for capability, patterns in self.capability_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                capabilities.add(capability)
        
        # Infer from risk signals
        for signal in risk_signals:
            signal_type = signal.get("signal_type")
            if signal_type == "monitoring":
                capabilities.add("continuous_monitoring")
            elif signal_type == "detection":
                capabilities.add("early_warning_detection")
        
        return sorted(list(capabilities))


class AlignmentAssessor:
    """Assess alignment between bill requirements and wireless sensing capabilities"""
    
    def assess_alignment(
        self,
        risk_signals: List[Dict[str, Any]],
        capabilities: List[str],
        risk_relevance: str
    ) -> Dict[str, Any]:
        """
        Assess alignment level and provide justification
        
        Returns:
            Dict with 'alignment_level' and 'justification'
        """
        if risk_relevance == "none" or not risk_signals:
            return {
                "alignment_level": "none",
                "justification": "Bill does not contain risk-relevant language or monitoring requirements."
            }
        
        # Count direct monitoring/detection signals
        direct_signals = [s for s in risk_signals if s.get("signal_type") in ["monitoring", "detection"]]
        indirect_signals = [s for s in risk_signals if s.get("signal_type") in ["reporting", "mitigation"]]
        
        # Assess alignment
        if len(direct_signals) >= 2 and len(capabilities) >= 2:
            alignment_level = "high"
            justification = (
                f"Bill contains {len(direct_signals)} direct monitoring/detection requirements "
                f"that align with wireless sensing capabilities: {', '.join(capabilities[:3])}. "
                f"Statutory language explicitly requires continuous observation or early warning systems."
            )
        elif len(direct_signals) >= 1 or (len(indirect_signals) >= 2 and len(capabilities) >= 1):
            alignment_level = "medium"
            justification = (
                f"Bill creates reporting or safety duties that could benefit from automated monitoring. "
                f"Identified capabilities: {', '.join(capabilities[:2])}. "
                f"Indirect fit: requirements enable but do not mandate sensing systems."
            )
        elif len(indirect_signals) >= 1 or risk_relevance == "latent":
            alignment_level = "low"
            justification = (
                f"Bill enables pilots, studies, or modernization that may create future opportunities. "
                f"Latent fit: potential application of sensing capabilities if programs are established."
            )
        else:
            alignment_level = "none"
            justification = "No clear connection between bill requirements and wireless sensing capabilities."
        
        return {
            "alignment_level": alignment_level,
            "justification": justification
        }


class TemporalContextAnalyzer:
    """Analyze temporal and political context (2026 midterm elections)"""
    
    def __init__(self):
        self.general_election_date = date(2026, 11, 3)
        self.primary_season_start = date(2026, 3, 1)
        self.primary_season_end = date(2026, 5, 31)
    
    def analyze_temporal_context(
        self,
        bill_metadata: Optional[Dict[str, Any]] = None,
        analysis_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Analyze temporal context based on bill status and election timing
        
        Args:
            bill_metadata: Optional dict with 'status', 'enactment_date', 'fiscal_year'
            analysis_date: Optional analysis date (defaults to today)
            
        Returns:
            Dict with temporal context fields
        """
        if analysis_date is None:
            analysis_date = date.today()
        
        bill_status = self._determine_bill_status(bill_metadata)
        
        context = {
            "bill_status": bill_status.value,
            "election_year": True,  # 2026 is election year
            "analysis_date": analysis_date.isoformat(),
            "general_election_date": self.general_election_date.isoformat()
        }
        
        if bill_status == BillStatus.PENDING:
            days_until_election = (self.general_election_date - analysis_date).days
            context["days_until_election"] = days_until_election
            context["timing_urgency"] = self._assess_urgency(days_until_election)
            context["political_viability"] = "medium"  # Default, could be enhanced
            context["election_year_dynamics"] = [
                "Bill may be used as campaign issue",
                "Control of Congress will change post-election",
                "Bills must pass before Nov 3 or risk reset"
            ]
            context["implementation_timeline_risk"] = (
                "Bills passed in 2026 may face implementation delays if control of Congress changes"
            )
        elif bill_status == BillStatus.ENACTED:
            if bill_metadata and "enactment_date" in bill_metadata:
                context["enactment_date"] = bill_metadata["enactment_date"]
            if bill_metadata and "fiscal_year" in bill_metadata:
                context["fiscal_year"] = bill_metadata["fiscal_year"]
            
            context["implementation_timeline"] = {
                "focus": "implementation_readiness",
                "note": "Bill is enacted; analysis focuses on deployment readiness"
            }
            context["implementation_risk"] = (
                "Post-election control change (Nov 2026) may affect agency implementation priorities"
            )
            context["timing_urgency"] = "low"  # Already passed
        else:  # HISTORICAL
            context["timing_urgency"] = "none"
            context["implementation_timeline"] = {
                "focus": "retrospective_analysis",
                "note": "Historical bill; used for pattern recognition"
            }
        
        return context
    
    def _determine_bill_status(self, bill_metadata: Optional[Dict[str, Any]]) -> BillStatus:
        """Determine bill status from metadata"""
        if not bill_metadata:
            return BillStatus.PENDING  # Default assumption
        
        status_str = bill_metadata.get("status", "").lower()
        if status_str == "enacted" or "enactment_date" in bill_metadata:
            return BillStatus.ENACTED
        elif status_str == "historical":
            return BillStatus.HISTORICAL
        else:
            return BillStatus.PENDING
    
    def _assess_urgency(self, days_until_election: int) -> str:
        """Assess timing urgency based on days until election"""
        if days_until_election < 90:
            return "high"
        elif days_until_election < 180:
            return "medium"
        else:
            return "low"


class BillRiskAnalyzer:
    """Main analyzer class that coordinates all components"""
    
    def __init__(self):
        self.parser = BillParser()
        self.structure_extractor = BillStructureExtractor()
        self.risk_extractor = RiskLanguageExtractor()
        self.capability_mapper = CapabilityMapper()
        self.alignment_assessor = AlignmentAssessor()
        self.temporal_analyzer = TemporalContextAnalyzer()
    
    def analyze(
        self,
        bill_file: Path,
        bill_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform complete bill risk analysis
        
        Args:
            bill_file: Path to bill file
            bill_metadata: Optional metadata (bill_id, status, enactment_date, etc.)
            
        Returns:
            Complete analysis result matching output schema
        """
        # Parse bill
        parsed = self.parser.parse(bill_file)
        
        # Extract structure
        structure = self.structure_extractor.extract_structure(parsed["text"])
        
        # Extract risk signals
        risk_signals = self.risk_extractor.extract_risk_signals(parsed["text"], structure)
        
        # Map capabilities
        capabilities = self.capability_mapper.map_capabilities(parsed["text"], risk_signals)
        
        # Determine risk relevance
        risk_relevance = self._determine_risk_relevance(risk_signals)
        
        # Assess alignment
        alignment = self.alignment_assessor.assess_alignment(
            risk_signals, capabilities, risk_relevance
        )
        
        # Analyze temporal context
        temporal_context = self.temporal_analyzer.analyze_temporal_context(bill_metadata)
        
        # Extract risk domains
        risk_domains = list(set(s.get("risk_domain") for s in risk_signals if s.get("risk_domain")))
        
        # Build section-by-section breakdown
        section_breakdown = self._build_section_breakdown(structure, risk_signals, capabilities)
        
        # Build result
        result = {
            "bill_id": bill_metadata.get("bill_id", "UNKNOWN") if bill_metadata else "UNKNOWN",
            "risk_relevance": risk_relevance,
            "risk_domains": risk_domains,
            "statutory_signals": risk_signals,
            "capability_requirements": capabilities,
            "wireless_risk_alignment": alignment,
            "temporal_context": temporal_context,
            "section_breakdown": section_breakdown,  # Enhanced: section-by-section analysis
            "notes": self._generate_notes(risk_signals, capabilities, temporal_context)
        }
        
        return result
    
    def _determine_risk_relevance(self, risk_signals: List[Dict[str, Any]]) -> str:
        """Determine overall risk relevance level"""
        if not risk_signals:
            return "none"
        
        direct_signals = [s for s in risk_signals if s.get("signal_type") in ["monitoring", "detection"]]
        if len(direct_signals) >= 2:
            return "direct"
        elif len(risk_signals) >= 1:
            return "indirect"
        else:
            return "latent"
    
    def _generate_notes(
        self,
        risk_signals: List[Dict[str, Any]],
        capabilities: List[str],
        temporal_context: Dict[str, Any]
    ) -> str:
        """Generate summary notes"""
        notes_parts = []
        
        if risk_signals:
            notes_parts.append(
                f"Bill contains {len(risk_signals)} risk-relevant signals requiring monitoring, "
                "detection, or reporting capabilities."
            )
        
        if capabilities:
            notes_parts.append(
                f"Identified {len(capabilities)} capability requirements that could be supported "
                "by wireless, low-power sensing systems."
            )
        
        if temporal_context.get("bill_status") == "pending":
            notes_parts.append(
                f"Election-year timing creates urgency for passage before Nov 3, 2026."
            )
        elif temporal_context.get("bill_status") == "enacted":
            notes_parts.append(
                "Bill is enacted; focus shifts to implementation readiness and deployment timelines."
            )
        
        return " ".join(notes_parts) if notes_parts else "No significant risk signals identified."
    
    def _build_section_breakdown(
        self,
        structure: Dict[str, Any],
        risk_signals: List[Dict[str, Any]],
        capabilities: List[str]
    ) -> List[Dict[str, Any]]:
        """Build section-by-section breakdown of analysis"""
        section_breakdown = []
        sections = structure.get("sections", [])
        
        # Group signals by section
        signals_by_section = {}
        for signal in risk_signals:
            section_num = signal.get("section", "Unknown")
            if section_num not in signals_by_section:
                signals_by_section[section_num] = []
            signals_by_section[section_num].append(signal)
        
        # Build breakdown for each section
        for section in sections:
            section_num = section.get("section_number", "Unknown")
            section_signals = signals_by_section.get(section_num, [])
            
            # Extract capabilities mentioned in this section
            section_text = section.get("full_text", section.get("text_excerpt", "")).lower()
            section_capabilities = [
                cap for cap in capabilities 
                if any(pattern in section_text for pattern in self.capability_mapper.capability_patterns.get(cap, []))
            ]
            
            if section_signals or section_capabilities:
                section_breakdown.append({
                    "section_number": section_num,
                    "section_title": section.get("title", ""),
                    "signal_count": len(section_signals),
                    "signals": section_signals[:5],  # Limit to top 5 signals per section
                    "capabilities": section_capabilities,
                    "risk_domains": list(set(s.get("risk_domain") for s in section_signals if s.get("risk_domain")))
                })
        
        return section_breakdown
