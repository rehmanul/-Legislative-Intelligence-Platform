"""
Command Reader Utility for Agents

Agents can use this to check for pending commands from dashboards.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def get_pending_commands(base_dir: Path, command_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get pending commands from commands directory.
    
    Args:
        base_dir: Base directory of agent-orchestrator
        command_type: Optional filter by command type (e.g., "approve", "trigger_agent")
    
    Returns:
        List of pending command dictionaries
    """
    commands_dir = base_dir / "commands"
    if not commands_dir.exists():
        return []
    
    pending_commands = []
    
    for command_file in commands_dir.glob("*.json"):
        try:
            command_data = json.loads(command_file.read_text(encoding="utf-8"))
            meta = command_data.get("_meta", {})
            
            # Check if command is pending
            if meta.get("status") != "pending":
                continue
            
            # Filter by type if specified
            if command_type and meta.get("command_type") != command_type:
                continue
            
            # Add file path for processing
            command_data["_file_path"] = str(command_file)
            pending_commands.append(command_data)
            
        except Exception as e:
            logger.warning(f"Failed to read command file {command_file}: {e}")
    
    return pending_commands


def mark_command_processed(base_dir: Path, command_file_path: str, result: Optional[Dict[str, Any]] = None):
    """
    Mark a command as processed.
    
    Args:
        base_dir: Base directory of agent-orchestrator
        command_file_path: Path to command file
        result: Optional result data to store
    """
    command_file = Path(command_file_path)
    if not command_file.exists():
        logger.warning(f"Command file not found: {command_file_path}")
        return
    
    try:
        command_data = json.loads(command_file.read_text(encoding="utf-8"))
        meta = command_data.get("_meta", {})
        
        meta["status"] = "processed"
        meta["processed_at"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        if result:
            command_data["result"] = result
        
        # Move to processed directory
        processed_dir = base_dir / "commands" / "processed"
        processed_dir.mkdir(exist_ok=True)
        
        processed_file = processed_dir / command_file.name
        processed_file.write_text(json.dumps(command_data, indent=2), encoding="utf-8")
        
        # Remove original
        command_file.unlink()
        
        logger.info(f"Command processed: {command_file.name}")
        
    except Exception as e:
        logger.error(f"Failed to mark command as processed: {e}")


def mark_command_failed(base_dir: Path, command_file_path: str, error: str):
    """
    Mark a command as failed.
    
    Args:
        base_dir: Base directory of agent-orchestrator
        command_file_path: Path to command file
        error: Error message
    """
    command_file = Path(command_file_path)
    if not command_file.exists():
        return
    
    try:
        command_data = json.loads(command_file.read_text(encoding="utf-8"))
        meta = command_data.get("_meta", {})
        
        meta["status"] = "failed"
        meta["failed_at"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        meta["error"] = error
        
        # Move to failed directory
        failed_dir = base_dir / "commands" / "failed"
        failed_dir.mkdir(exist_ok=True)
        
        failed_file = failed_dir / command_file.name
        failed_file.write_text(json.dumps(command_data, indent=2), encoding="utf-8")
        
        # Remove original
        command_file.unlink()
        
        logger.warning(f"Command failed: {command_file.name} - {error}")
        
    except Exception as e:
        logger.error(f"Failed to mark command as failed: {e}")
