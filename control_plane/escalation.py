"""
Escalation Handler - Deterministic escalation logic.

This module handles escalation triggers and logs critical failures.
"""

import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class EscalationHandler:
    """Deterministic escalation handling."""
    
    # Escalation thresholds
    CONFIDENCE_THRESHOLD = 0.70  # 70%
    ASSUMPTION_DRIFT_THRESHOLD = 0.20  # 20%
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize escalation handler.
        
        Args:
            base_dir: Base directory for logs (defaults to agent-orchestrator root)
        """
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        
        self.base_dir = Path(base_dir)
        self.logs_dir = self.base_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        self.escalation_log = self.logs_dir / "escalation_log.jsonl"
    
    def escalate(
        self,
        reason: str,
        severity: str = "MEDIUM",
        context: Optional[Dict[str, Any]] = None,
        confidence: Optional[float] = None,
        assumption_drift: Optional[float] = None
    ) -> None:
        """
        Escalate an issue with deterministic triggers.
        
        Escalation triggers:
        - confidence < CONFIDENCE_THRESHOLD (70%)
        - gate bypass detected
        - assumption_drift > ASSUMPTION_DRIFT_THRESHOLD (20%)
        - Explicit escalation request
        
        Args:
            reason: Human-readable escalation reason
            severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL)
            context: Additional context dictionary
            confidence: Confidence score (0.0-1.0) if applicable
            assumption_drift: Assumption drift percentage (0.0-1.0) if applicable
        """
        escalation_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": severity.upper(),
            "reason": reason,
            "context": context or {},
            "confidence": confidence,
            "assumption_drift": assumption_drift,
            "triggers": self._determine_triggers(confidence, assumption_drift, reason)
        }
        
        # Log to escalation log file
        try:
            with open(self.escalation_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(escalation_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"[EscalationHandler] Failed to write escalation log: {e}", exc_info=True)
        
        # Log to application logger based on severity
        log_level = self._severity_to_log_level(severity)
        log_msg = f"[ESCALATION {severity}] {reason}"
        if context:
            log_msg += f" | Context: {context}"
        
        logger.log(log_level, log_msg)
        
        # For CRITICAL severity, also log to stderr
        if severity.upper() == "CRITICAL":
            import sys
            print(f"CRITICAL ESCALATION: {reason}", file=sys.stderr)
    
    def log_critical_failure(
        self,
        error_code: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a critical failure (always escalates as CRITICAL).
        
        Args:
            error_code: Error code identifier
            message: Human-readable error message
            context: Additional context
        """
        self.escalate(
            reason=f"Critical failure: {error_code} - {message}",
            severity="CRITICAL",
            context={
                "error_code": error_code,
                "message": message,
                **(context or {})
            }
        )
    
    def check_confidence_threshold(self, confidence: float) -> bool:
        """
        Check if confidence is below threshold (should escalate).
        
        Args:
            confidence: Confidence score (0.0-1.0)
            
        Returns:
            True if below threshold (should escalate), False otherwise
        """
        return confidence < self.CONFIDENCE_THRESHOLD
    
    def check_assumption_drift(self, assumption_drift: float) -> bool:
        """
        Check if assumption drift exceeds threshold (should escalate).
        
        Args:
            assumption_drift: Assumption drift percentage (0.0-1.0)
            
        Returns:
            True if exceeds threshold (should escalate), False otherwise
        """
        return assumption_drift > self.ASSUMPTION_DRIFT_THRESHOLD
    
    def _determine_triggers(
        self,
        confidence: Optional[float],
        assumption_drift: Optional[float],
        reason: str
    ) -> list[str]:
        """Determine which triggers caused escalation."""
        triggers = []
        
        if confidence is not None and self.check_confidence_threshold(confidence):
            triggers.append("LOW_CONFIDENCE")
        
        if assumption_drift is not None and self.check_assumption_drift(assumption_drift):
            triggers.append("HIGH_ASSUMPTION_DRIFT")
        
        reason_lower = reason.lower()
        if "bypass" in reason_lower or "gate" in reason_lower:
            triggers.append("GATE_BYPASS")
        
        if "violation" in reason_lower:
            triggers.append("VIOLATION")
        
        if not triggers:
            triggers.append("EXPLICIT_ESCALATION")
        
        return triggers
    
    def _severity_to_log_level(self, severity: str) -> int:
        """Convert severity string to logging level."""
        severity_map = {
            "LOW": logging.INFO,
            "MEDIUM": logging.WARNING,
            "HIGH": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return severity_map.get(severity.upper(), logging.WARNING)
