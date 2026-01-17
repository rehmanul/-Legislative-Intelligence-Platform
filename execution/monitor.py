"""
Execution Monitor - Activity Tracking.

Provides append-only JSONL logging for all execution activities.
Tracks execution lifecycle events.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from .models import (
    ExecutionActivity,
    ExecutionStatus,
    ExecutionRequest,
    ExecutionResult
)
from .config import ACTIVITY_LOG_FILE

logger = logging.getLogger(__name__)


class ExecutionMonitor:
    """
    Monitors and logs execution activities.
    
    Provides append-only JSONL logging for compliance and audit.
    """
    
    def __init__(self):
        """Initialize execution monitor."""
        self._ensure_log_file()
    
    def _ensure_log_file(self) -> None:
        """Ensure activity log file exists."""
        ACTIVITY_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not ACTIVITY_LOG_FILE.exists():
            # Create empty file
            ACTIVITY_LOG_FILE.touch()
    
    def log_activity(
        self,
        execution_id: str,
        event_type: str,
        workflow_id: str,
        status: ExecutionStatus,
        message: str,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ExecutionActivity:
        """
        Log execution activity.
        
        Args:
            execution_id: Execution identifier
            event_type: Event type (execution_requested, execution_approved, etc.)
            workflow_id: Workflow identifier
            status: Execution status
            message: Activity message
            agent_id: Agent identifier (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            ExecutionActivity record
        """
        activity = ExecutionActivity(
            execution_id=execution_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            workflow_id=workflow_id,
            agent_id=agent_id,
            status=status,
            message=message,
            metadata=metadata or {}
        )
        
        # Append to JSONL file
        try:
            with open(ACTIVITY_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(activity.dict(), default=str) + "\n")
            
            logger.debug(
                f"Execution activity logged: {event_type} for {execution_id}"
            )
        except Exception as e:
            logger.error(f"Failed to log execution activity: {e}")
        
        return activity
    
    def log_execution_requested(
        self,
        request: ExecutionRequest
    ) -> ExecutionActivity:
        """
        Log execution request.
        
        Args:
            request: Execution request
            
        Returns:
            ExecutionActivity record
        """
        return self.log_activity(
            execution_id=request.execution_id,
            event_type="execution_requested",
            workflow_id=request.workflow_id,
            status=ExecutionStatus.PENDING,
            message=f"Execution requested: {request.action_type.value} to {request.target}",
            agent_id=request.agent_id,
            metadata={
                "action_type": request.action_type.value,
                "target": request.target,
                "requires_approval": request.requires_approval,
                "dry_run": request.dry_run
            }
        )
    
    def log_execution_approved(
        self,
        execution_id: str,
        workflow_id: str,
        approved_by: str,
        agent_id: Optional[str] = None
    ) -> ExecutionActivity:
        """
        Log execution approval.
        
        Args:
            execution_id: Execution identifier
            workflow_id: Workflow identifier
            approved_by: Human identifier
            agent_id: Agent identifier (optional)
            
        Returns:
            ExecutionActivity record
        """
        return self.log_activity(
            execution_id=execution_id,
            event_type="execution_approved",
            workflow_id=workflow_id,
            status=ExecutionStatus.APPROVED,
            message=f"Execution approved by {approved_by}",
            agent_id=agent_id,
            metadata={"approved_by": approved_by}
        )
    
    def log_execution_executed(
        self,
        execution_id: str,
        workflow_id: str,
        result: ExecutionResult,
        agent_id: Optional[str] = None
    ) -> ExecutionActivity:
        """
        Log execution completion.
        
        Args:
            execution_id: Execution identifier
            workflow_id: Workflow identifier
            result: Execution result
            agent_id: Agent identifier (optional)
            
        Returns:
            ExecutionActivity record
        """
        status = ExecutionStatus.EXECUTED if result.success else ExecutionStatus.FAILED
        
        return self.log_activity(
            execution_id=execution_id,
            event_type="execution_executed",
            workflow_id=workflow_id,
            status=status,
            message=f"Execution {'succeeded' if result.success else 'failed'}",
            agent_id=agent_id,
            metadata={
                "success": result.success,
                "dry_run": result.dry_run,
                "message_id": result.message_id,
                "error": result.error,
                "error_code": result.error_code
            }
        )
    
    def log_execution_failed(
        self,
        execution_id: str,
        workflow_id: str,
        error: str,
        error_code: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> ExecutionActivity:
        """
        Log execution failure.
        
        Args:
            execution_id: Execution identifier
            workflow_id: Workflow identifier
            error: Error message
            error_code: Error code (optional)
            agent_id: Agent identifier (optional)
            
        Returns:
            ExecutionActivity record
        """
        return self.log_activity(
            execution_id=execution_id,
            event_type="execution_failed",
            workflow_id=workflow_id,
            status=ExecutionStatus.FAILED,
            message=f"Execution failed: {error}",
            agent_id=agent_id,
            metadata={
                "error": error,
                "error_code": error_code
            }
        )
    
    def log_execution_terminated(
        self,
        execution_id: str,
        workflow_id: str,
        reason: str,
        terminated_by: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> ExecutionActivity:
        """
        Log execution termination.
        
        Args:
            execution_id: Execution identifier
            workflow_id: Workflow identifier
            reason: Termination reason
            terminated_by: Human or system identifier (optional)
            agent_id: Agent identifier (optional)
            
        Returns:
            ExecutionActivity record
        """
        return self.log_activity(
            execution_id=execution_id,
            event_type="execution_terminated",
            workflow_id=workflow_id,
            status=ExecutionStatus.TERMINATED,
            message=f"Execution terminated: {reason}",
            agent_id=agent_id,
            metadata={
                "reason": reason,
                "terminated_by": terminated_by
            }
        )
    
    def get_activity_log(
        self,
        workflow_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[ExecutionActivity]:
        """
        Get activity log entries.
        
        Args:
            workflow_id: Filter by workflow (optional)
            execution_id: Filter by execution (optional)
            limit: Maximum number of entries (optional)
            
        Returns:
            List of ExecutionActivity records
        """
        activities = []
        
        if not ACTIVITY_LOG_FILE.exists():
            return activities
        
        try:
            with open(ACTIVITY_LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        activity = ExecutionActivity(**data)
                        
                        # Apply filters
                        if workflow_id and activity.workflow_id != workflow_id:
                            continue
                        if execution_id and activity.execution_id != execution_id:
                            continue
                        
                        activities.append(activity)
                    except Exception as e:
                        logger.warning(f"Failed to parse activity log line: {e}")
                        continue
            
            # Sort by timestamp (newest first)
            activities.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Apply limit
            if limit:
                activities = activities[:limit]
            
        except Exception as e:
            logger.error(f"Failed to read activity log: {e}")
        
        return activities


# Global monitor instance
_monitor: Optional[ExecutionMonitor] = None


def get_monitor() -> ExecutionMonitor:
    """
    Get global execution monitor instance.
    
    Returns:
        ExecutionMonitor instance
    """
    global _monitor
    if _monitor is None:
        _monitor = ExecutionMonitor()
    return _monitor
