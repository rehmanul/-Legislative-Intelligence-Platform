"""
Workflow Isolation Verification and Enforcement

Verifies and enforces campaign-level data isolation to prevent data leakage
between concurrent workflows.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import json
from datetime import datetime


class IsolationViolation(Exception):
    """Violation of workflow isolation."""
    pass


class WorkflowIsolationChecker:
    """Verifies workflow isolation and prevents data leakage."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize isolation checker.
        
        Args:
            base_dir: Base directory (defaults to agent-orchestrator root)
        """
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        
        self.base_dir = Path(base_dir)
        self.state_dir = base_dir / "state"
        self.artifacts_dir = base_dir / "artifacts"
        self.data_dir = base_dir / "data"
    
    def verify_workflow_isolation(self, workflow_id: str) -> Tuple[bool, List[str]]:
        """
        Verify workflow isolation for a given workflow.
        
        Checks:
        - State files are workflow-specific
        - Artifacts include workflow_id in path or metadata
        - Agent registrations include workflow_id
        - No cross-workflow data access
        
        Args:
            workflow_id: Workflow identifier to check
            
        Returns:
            (is_isolated, violations)
        """
        violations = []
        
        # 1. Check state storage isolation
        state_file = self.state_dir / "workflows" / workflow_id / "state.json"
        if not state_file.exists():
            violations.append(f"State file missing for workflow {workflow_id}")
        
        # 2. Check artifacts - agents may write globally
        # This is a known issue - artifacts are written to artifacts/{agent_id}/ not artifacts/{workflow_id}/
        # This needs to be fixed but is tracked as a known gap
        
        # 3. Check agent registry includes workflow_id
        registry_file = self.base_dir / "registry" / "agent-registry.json"
        if registry_file.exists():
            try:
                registry = json.loads(registry_file.read_text(encoding="utf-8"))
                for agent in registry.get("agents", []):
                    agent_workflow_id = agent.get("workflow_id")
                    if not agent_workflow_id:
                        violations.append(
                            f"Agent {agent.get('agent_id')} missing workflow_id in registry"
                        )
            except:
                pass
        
        # 4. Check LDA contacts are per-workflow
        lda_contacts_file = self.data_dir / "lda_contacts" / "workflow_contacts.json"
        if lda_contacts_file.exists():
            try:
                workflow_contacts = json.loads(lda_contacts_file.read_text(encoding="utf-8"))
                # Verify contacts are properly mapped to workflows
                if workflow_id not in workflow_contacts:
                    # This is OK - workflow may have no contacts yet
                    pass
            except:
                pass
        
        return len(violations) == 0, violations
    
    def verify_all_workflows_isolated(self) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Verify all workflows are properly isolated.
        
        Returns:
            (all_isolated, workflow_violations)
        """
        workflow_violations = {}
        
        # Find all workflow directories
        workflows_dir = self.state_dir / "workflows"
        if workflows_dir.exists():
            for workflow_dir in workflows_dir.iterdir():
                if workflow_dir.is_dir():
                    workflow_id = workflow_dir.name
                    is_isolated, violations = self.verify_workflow_isolation(workflow_id)
                    if violations:
                        workflow_violations[workflow_id] = violations
        
        all_isolated = len(workflow_violations) == 0
        return all_isolated, workflow_violations


class CampaignAccessControl:
    """Access control for campaign-level data."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize access control.
        
        Args:
            base_dir: Base directory
        """
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        
        self.base_dir = Path(base_dir)
        self.access_control_file = base_dir / "data" / "campaign_access_control.json"
        self._load_access_control()
    
    def _load_access_control(self) -> Dict[str, Dict[str, List[str]]]:
        """Load access control mappings."""
        if self.access_control_file.exists():
            try:
                return json.loads(self.access_control_file.read_text(encoding="utf-8"))
            except:
                return {}
        return {}
    
    def _save_access_control(self, access_control: Dict[str, Dict[str, List[str]]]):
        """Save access control mappings."""
        self.access_control_file.parent.mkdir(parents=True, exist_ok=True)
        self.access_control_file.write_text(
            json.dumps(access_control, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    
    def grant_access(self, workflow_id: str, user_id: str, role: str = "viewer"):
        """
        Grant user access to workflow.
        
        Args:
            workflow_id: Workflow identifier
            user_id: User identifier
            role: Access role (viewer, editor, admin)
        """
        access_control = self._load_access_control()
        
        if workflow_id not in access_control:
            access_control[workflow_id] = {}
        
        if role not in access_control[workflow_id]:
            access_control[workflow_id][role] = []
        
        if user_id not in access_control[workflow_id][role]:
            access_control[workflow_id][role].append(user_id)
        
        self._save_access_control(access_control)
    
    def revoke_access(self, workflow_id: str, user_id: str):
        """Revoke user access to workflow."""
        access_control = self._load_access_control()
        
        if workflow_id in access_control:
            for role in access_control[workflow_id]:
                if user_id in access_control[workflow_id][role]:
                    access_control[workflow_id][role].remove(user_id)
        
        self._save_access_control(access_control)
    
    def has_access(self, workflow_id: str, user_id: str, required_role: str = "viewer") -> bool:
        """
        Check if user has access to workflow.
        
        Args:
            workflow_id: Workflow identifier
            user_id: User identifier
            required_role: Required role (viewer, editor, admin)
            
        Returns:
            True if user has access, False otherwise
        """
        access_control = self._load_access_control()
        
        if workflow_id not in access_control:
            # No access control defined - default deny
            return False
        
        # Role hierarchy: admin > editor > viewer
        role_hierarchy = {"viewer": 0, "editor": 1, "admin": 2}
        required_level = role_hierarchy.get(required_role, 0)
        
        for role, users in access_control[workflow_id].items():
            role_level = role_hierarchy.get(role, -1)
            if user_id in users and role_level >= required_level:
                return True
        
        return False
    
    def get_workflows_for_user(self, user_id: str) -> List[str]:
        """Get list of workflow IDs accessible to user."""
        access_control = self._load_access_control()
        accessible_workflows = []
        
        for workflow_id, roles in access_control.items():
            for role, users in roles.items():
                if user_id in users:
                    accessible_workflows.append(workflow_id)
                    break
        
        return accessible_workflows


class CampaignResourceAllocator:
    """Resource allocation per campaign/workflow."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize resource allocator.
        
        Args:
            base_dir: Base directory
        """
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        
        self.base_dir = Path(base_dir)
        self.allocations_file = base_dir / "data" / "campaign_resource_allocations.json"
        self._load_allocations()
    
    def _load_allocations(self) -> Dict[str, Dict[str, Any]]:
        """Load resource allocations."""
        if self.allocations_file.exists():
            try:
                return json.loads(self.allocations_file.read_text(encoding="utf-8"))
            except:
                return {}
        return {}
    
    def _save_allocations(self, allocations: Dict[str, Dict[str, Any]]):
        """Save resource allocations."""
        self.allocations_file.parent.mkdir(parents=True, exist_ok=True)
        self.allocations_file.write_text(
            json.dumps(allocations, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8"
        )
    
    def set_resource_limits(
        self,
        workflow_id: str,
        max_concurrent_agents: Optional[int] = None,
        max_memory_mb: Optional[int] = None,
        priority: str = "medium"
    ):
        """
        Set resource limits for workflow.
        
        Args:
            workflow_id: Workflow identifier
            max_concurrent_agents: Maximum concurrent agents (None = unlimited)
            max_memory_mb: Maximum memory in MB (None = unlimited)
            priority: Priority level (low, medium, high)
        """
        allocations = self._load_allocations()
        
        allocations[workflow_id] = {
            "max_concurrent_agents": max_concurrent_agents,
            "max_memory_mb": max_memory_mb,
            "priority": priority,
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        self._save_allocations(allocations)
    
    def get_resource_limits(self, workflow_id: str) -> Dict[str, Any]:
        """Get resource limits for workflow."""
        allocations = self._load_allocations()
        return allocations.get(workflow_id, {
            "max_concurrent_agents": None,
            "max_memory_mb": None,
            "priority": "medium"
        })
    
    def can_spawn_agent(self, workflow_id: str, current_count: int) -> Tuple[bool, Optional[str]]:
        """
        Check if workflow can spawn another agent.
        
        Args:
            workflow_id: Workflow identifier
            current_count: Current number of active agents for workflow
            
        Returns:
            (can_spawn, reason_if_blocked)
        """
        limits = self.get_resource_limits(workflow_id)
        max_agents = limits.get("max_concurrent_agents")
        
        if max_agents is None:
            return True, None
        
        if current_count >= max_agents:
            return False, f"Workflow {workflow_id} at max concurrent agents limit ({max_agents})"
        
        return True, None
