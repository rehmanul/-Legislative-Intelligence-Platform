"""
Base Agent Class - Foundation for all agent types in the orchestration system.

This module provides the abstract base class that all specialized agents inherit from.
It handles workflow context management, entry/output path resolution, and execution lifecycle.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentBase(ABC):
    """
    Abstract base class for all agents in the orchestration system.
    
    Provides:
    - Workflow context management
    - Entry/output path resolution
    - Execution lifecycle with stop conditions
    - Artifact persistence
    """
    
    # Class-level configuration (to be overridden by subclasses)
    AGENT_ID: str = "base_agent"
    ENTRY_PATH: str = ""
    OUTPUT_PATH: str = ""
    RESPONSIBILITY: str = ""
    FORBIDDEN: List[str] = []
    
    def __init__(self, workflow_id: str, base_dir: Optional[Path] = None):
        """
        Initialize the agent with a workflow context.
        
        Args:
            workflow_id: Unique identifier for the workflow
            base_dir: Base directory for data storage (defaults to parent of agents/)
        """
        self.workflow_id = workflow_id
        self.base_dir = base_dir or Path(__file__).parent.parent.parent
        self.data_dir = self.base_dir / "data"
        self.artifacts_dir = self.base_dir / "artifacts"
        self.workflow_context: Dict[str, Any] = {}
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"[{self.AGENT_ID}] Initialized for workflow: {workflow_id}")
    
    def read_entry(self) -> Dict[str, Any]:
        """
        Read data from the entry path specified in ENTRY_PATH.
        
        Returns:
            Dictionary containing the entry data, or empty dict if not found.
        """
        try:
            # Parse entry path (e.g., "context.raw_inputs" -> ["context", "raw_inputs"])
            path_parts = self.ENTRY_PATH.split(".")
            
            # Look for workflow state file
            state_file = self.data_dir / "workflow_state.json"
            if state_file.exists():
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                
                # Navigate the path
                current = state
                for part in path_parts:
                    if part == "*":
                        # Wildcard - return current level
                        break
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        logger.warning(f"[{self.AGENT_ID}] Path '{self.ENTRY_PATH}' not found in state")
                        return {}
                
                return current if isinstance(current, dict) else {"value": current}
            
            logger.info(f"[{self.AGENT_ID}] No workflow state file found, returning empty entry")
            return {}
            
        except Exception as e:
            logger.error(f"[{self.AGENT_ID}] Error reading entry: {e}")
            return {}
    
    def write_output(self, data: Dict[str, Any]) -> Path:
        """
        Write data to the output path specified in OUTPUT_PATH.
        
        Args:
            data: The output data to persist
            
        Returns:
            Path to the written artifact
        """
        try:
            # Create artifact directory for this agent
            agent_artifact_dir = self.artifacts_dir / self.AGENT_ID
            agent_artifact_dir.mkdir(parents=True, exist_ok=True)
            
            # Create timestamped output file
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_file = agent_artifact_dir / f"output_{timestamp}.json"
            
            # Add metadata
            output_data = {
                "_meta": {
                    "agent_id": self.AGENT_ID,
                    "workflow_id": self.workflow_id,
                    "output_path": self.OUTPUT_PATH,
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                    "responsibility": self.RESPONSIBILITY,
                },
                "data": data
            }
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, default=str)
            
            logger.info(f"[{self.AGENT_ID}] Output written to: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"[{self.AGENT_ID}] Error writing output: {e}")
            raise
    
    def update_workflow_state(self, data: Dict[str, Any]) -> None:
        """
        Update the workflow state file with the agent's output.
        
        Args:
            data: The data to merge into the workflow state
        """
        try:
            state_file = self.data_dir / "workflow_state.json"
            
            # Load existing state or create new
            if state_file.exists():
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
            else:
                state = {}
            
            # Navigate to output path and set data
            path_parts = self.OUTPUT_PATH.split(".")
            current = state
            
            for i, part in enumerate(path_parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Set the final value
            if path_parts:
                current[path_parts[-1]] = data
            
            # Write updated state
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, default=str)
            
            logger.info(f"[{self.AGENT_ID}] Workflow state updated at path: {self.OUTPUT_PATH}")
            
        except Exception as e:
            logger.error(f"[{self.AGENT_ID}] Error updating workflow state: {e}")
    
    @abstractmethod
    def _is_stop_condition_met(self, output_value: Any) -> bool:
        """
        Check if the agent's stop condition is satisfied.
        
        Args:
            output_value: The output data to validate
            
        Returns:
            True if stop condition is met, False otherwise
        """
        pass
    
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """
        Execute the agent's core logic.
        
        Returns:
            Dictionary containing the agent's output
        """
        pass
    
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate that the output doesn't contain forbidden content.
        
        Args:
            output: The output to validate
            
        Returns:
            True if output is valid, False otherwise
        """
        if not self.FORBIDDEN:
            return True
        
        output_str = json.dumps(output).lower()
        for forbidden in self.FORBIDDEN:
            if forbidden.lower() in output_str:
                logger.warning(f"[{self.AGENT_ID}] Output contains forbidden content: {forbidden}")
                return False
        
        return True
    
    def main(self) -> Optional[Path]:
        """
        Main execution entry point for the agent.
        
        Orchestrates:
        1. Execute agent logic
        2. Validate output
        3. Check stop condition
        4. Persist output
        
        Returns:
            Path to the output artifact, or None if execution failed
        """
        try:
            logger.info(f"[{self.AGENT_ID}] Starting execution for workflow: {self.workflow_id}")
            
            # Execute agent logic
            output = self.execute()
            
            # Validate output
            if not self.validate_output(output):
                logger.error(f"[{self.AGENT_ID}] Output validation failed")
                return None
            
            # Check stop condition
            if not self._is_stop_condition_met(output):
                logger.warning(f"[{self.AGENT_ID}] Stop condition not met")
                # Still persist output but mark as incomplete
                output["_incomplete"] = True
            
            # Persist output
            output_path = self.write_output(output)
            
            # Update workflow state
            self.update_workflow_state(output)
            
            logger.info(f"[{self.AGENT_ID}] Execution completed successfully")
            return output_path
            
        except Exception as e:
            logger.error(f"[{self.AGENT_ID}] Execution failed: {e}")
            return None
