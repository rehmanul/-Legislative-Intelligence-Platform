"""
Authorization Engine - Pre-Execution Approval System.

Classifies authorization requests and applies policy-based auto-approval rules.
Supports time-based escalation and confidence-based routing.
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

# Path setup
BASE_DIR = Path(__file__).parent.parent
POLICY_PATH = BASE_DIR / "config" / "authorization_policy.json"
AUDIT_LOG_PATH = BASE_DIR / "audit" / "audit-log.jsonl"

logger = logging.getLogger(__name__)


class AuthorizationDecision(str, Enum):
    """Authorization decision types."""
    AUTO_APPROVED = "AUTO_APPROVED"
    APPROVED_TIMEOUT = "APPROVED_TIMEOUT"
    ESCALATED = "ESCALATED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    REJECTED = "REJECTED"


class AuthorizationEngine:
    """
    Authorization decision engine.
    
    Classifies authorization requests and applies policy rules.
    """
    
    def __init__(self, policy_path: Optional[Path] = None):
        """Initialize authorization engine with policy."""
        self.policy_path = policy_path or POLICY_PATH
        self.policy = self._load_policy()
    
    def _load_policy(self) -> Dict[str, Any]:
        """Load authorization policy from file."""
        if not self.policy_path.exists():
            logger.warning(f"Policy file not found: {self.policy_path}. Using defaults.")
            return self._default_policy()
        
        try:
            with open(self.policy_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load policy: {e}. Using defaults.")
            return self._default_policy()
    
    def _default_policy(self) -> Dict[str, Any]:
        """Default policy if file not found."""
        return {
            "auto_approval_rules": {
                "routine": {"enabled": False},
                "contextual_timeout": {"enabled": False}
            },
            "confidence_thresholds": {
                "auto_approve": 0.9,
                "timeout_approve": 0.8
            },
            "escalation_timers": {
                "warning_minutes": 5,
                "timeout_approve_minutes": 15,
                "urgent_alert_minutes": 30
            }
        }
    
    def classify_authorization(
        self,
        agent_id: str,
        agent_metadata: Dict[str, Any],
        blocked_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Classify authorization request and determine decision.
        
        Args:
            agent_id: Agent identifier
            agent_metadata: Agent metadata including risk_level, confidence, etc.
            blocked_at: When agent was blocked (for time-based escalation)
            
        Returns:
            Decision dictionary with action, reason, and metadata
        """
        risk_level = agent_metadata.get("risk_level", "UNKNOWN").upper()
        confidence = agent_metadata.get("authorization_metadata", {}).get("confidence", 0.5)
        dry_run = agent_metadata.get("dry_run_mode", False)
        external_comm = agent_metadata.get("external_communication", False)
        
        # Check routine auto-approval
        routine_result = self._check_routine_approval(
            risk_level, confidence, dry_run, external_comm
        )
        if routine_result["eligible"]:
            return {
                "decision": AuthorizationDecision.AUTO_APPROVED,
                "reason": "routine",
                "rule": "routine",
                "confidence": confidence,
                "action": "APPROVE_IMMEDIATELY",
                "metadata": routine_result
            }
        
        # Check time-based escalation
        if blocked_at:
            escalation_result = self._check_escalation(
                risk_level, confidence, blocked_at, external_comm
            )
            if escalation_result["action"] != "NONE":
                return escalation_result
        
        # Determine if manual review required
        manual_review = self._requires_manual_review(risk_level, external_comm, agent_metadata)
        
        return {
            "decision": AuthorizationDecision.MANUAL_REVIEW_REQUIRED,
            "reason": "manual_review_required",
            "action": "REQUIRE_MANUAL_REVIEW",
            "confidence": confidence,
            "metadata": {
                "risk_level": risk_level,
                "external_communication": external_comm,
                "dry_run_mode": dry_run
            }
        }
    
    def _check_routine_approval(
        self,
        risk_level: str,
        confidence: float,
        dry_run: bool,
        external_comm: bool
    ) -> Dict[str, Any]:
        """Check if agent qualifies for routine auto-approval."""
        routine_rule = self.policy.get("auto_approval_rules", {}).get("routine", {})
        
        if not routine_rule.get("enabled", False):
            return {"eligible": False, "reason": "routine_rule_disabled"}
        
        # Check conditions
        conditions_met = (
            dry_run is True and
            risk_level == "LOW" and
            not external_comm
        )
        
        if conditions_met:
            return {
                "eligible": True,
                "reason": "routine_conditions_met",
                "rule": "routine"
            }
        
        return {"eligible": False, "reason": "routine_conditions_not_met"}
    
    def _check_escalation(
        self,
        risk_level: str,
        confidence: float,
        blocked_at: datetime,
        external_comm: bool
    ) -> Dict[str, Any]:
        """Check time-based escalation status."""
        timers = self.policy.get("escalation_timers", {})
        timeout_minutes = timers.get("timeout_approve_minutes", 15)
        urgent_minutes = timers.get("urgent_alert_minutes", 30)
        warning_minutes = timers.get("warning_minutes", 5)
        
        now = datetime.now(timezone.utc)
        minutes_blocked = (now - blocked_at).total_seconds() / 60
        
        # Urgent alert (no auto-approval for HIGH risk)
        if minutes_blocked >= urgent_minutes and risk_level == "HIGH":
            return {
                "decision": AuthorizationDecision.ESCALATED,
                "reason": "urgent_alert",
                "action": "ALERT_OPERATOR",
                "priority": "URGENT",
                "minutes_blocked": minutes_blocked,
                "auto_approve": False
            }
        
        # Timeout auto-approval (MEDIUM risk)
        timeout_rule = self.policy.get("auto_approval_rules", {}).get("contextual_timeout", {})
        if (
            minutes_blocked >= timeout_minutes and
            risk_level == "MEDIUM" and
            confidence >= self.policy.get("confidence_thresholds", {}).get("timeout_approve", 0.8) and
            timeout_rule.get("enabled", False) and
            not external_comm
        ):
            return {
                "decision": AuthorizationDecision.APPROVED_TIMEOUT,
                "reason": "contextual_timeout",
                "action": "AUTO_APPROVE",
                "priority": "MEDIUM",
                "minutes_blocked": minutes_blocked,
                "auto_approve": True,
                "notify_operator": timeout_rule.get("notify_operator", True)
            }
        
        # Warning (no action, just logging)
        if minutes_blocked >= warning_minutes:
            return {
                "decision": AuthorizationDecision.ESCALATED,
                "reason": "warning",
                "action": "WARN",
                "priority": "LOW",
                "minutes_blocked": minutes_blocked,
                "auto_approve": False
            }
        
        return {"action": "NONE", "priority": "NONE"}
    
    def _requires_manual_review(
        self,
        risk_level: str,
        external_comm: bool,
        agent_metadata: Dict[str, Any]
    ) -> bool:
        """Check if manual review is required."""
        manual_rules = self.policy.get("manual_review_required", {}).get("always_manual", {})
        conditions = manual_rules.get("conditions", [])
        
        # Check if any condition matches
        if risk_level == "HIGH" and external_comm:
            return True
        
        if agent_metadata.get("first_time_agent", False):
            return True
        
        if agent_metadata.get("new_stakeholders", False):
            return True
        
        return False
    
    def is_action_reversible(self, action_type: str, metadata: Dict[str, Any]) -> bool:
        """Check if action can be safely auto-approved (reversible)."""
        reversibility = self.policy.get("reversibility_rules", {})
        always_reversible = reversibility.get("always_reversible", [])
        always_irreversible = reversibility.get("always_irreversible", [])
        
        if action_type in always_reversible:
            return True
        
        if action_type in always_irreversible:
            return False
        
        # Check metadata flags
        if metadata.get("irreversible_flag", False):
            return False
        
        if metadata.get("external_communication", False):
            return False
        
        return True
    
    def log_authorization_decision(
        self,
        agent_id: str,
        decision: AuthorizationDecision,
        reason: str,
        metadata: Dict[str, Any],
        authorized_by: str = "system:authorization_engine"
    ) -> None:
        """Log authorization decision to audit trail."""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "event_type": "authorization_decision",
            "agent_id": agent_id,
            "decision": decision.value,
            "reason": reason,
            "authorized_by": authorized_by,
            **metadata
        }
        
        try:
            AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"Failed to log authorization decision: {e}")


def get_authorization_engine() -> AuthorizationEngine:
    """Get singleton authorization engine instance."""
    if not hasattr(get_authorization_engine, "_instance"):
        get_authorization_engine._instance = AuthorizationEngine()
    return get_authorization_engine._instance
