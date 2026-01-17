"""
EXEC_RUN Channel Abstraction.

Provides abstract interface for all execution channels (email, phone, SMS, etc.).
All execution must short-circuit in dry-run mode.
"""

from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime

from .models import (
    ExecutionRequest,
    ExecutionResult,
    ValidationResult,
    ExecutionStatusResponse,
    ChannelType
)
from .config import DRY_RUN_MODE


class ExecutionChannel(ABC):
    """
    Base class for execution channels.
    
    All channels must implement execute(), validate(), and get_status().
    Execution is short-circuited in dry-run mode.
    """
    
    def __init__(self, channel_type: ChannelType):
        """
        Initialize execution channel.
        
        Args:
            channel_type: Type of channel (EMAIL, PHONE, etc.)
        """
        self.channel_type = channel_type
        self.dry_run = DRY_RUN_MODE
    
    @abstractmethod
    def execute(
        self,
        request: ExecutionRequest,
        dry_run: Optional[bool] = None
    ) -> ExecutionResult:
        """
        Execute an action through this channel.
        
        Args:
            request: Execution request
            dry_run: Override global dry-run mode (defaults to config)
            
        Returns:
            ExecutionResult with success status and details
            
        Note:
            In dry-run mode, this should log the action but not send.
        """
        pass
    
    @abstractmethod
    def validate(self, request: ExecutionRequest) -> ValidationResult:
        """
        Validate an execution request.
        
        Args:
            request: Execution request to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        pass
    
    @abstractmethod
    def get_status(self, execution_id: str) -> ExecutionStatusResponse:
        """
        Get status of an execution.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            ExecutionStatusResponse with current status
        """
        pass
    
    def _should_execute(self, request: ExecutionRequest, dry_run: Optional[bool] = None) -> bool:
        """
        Determine if execution should proceed (not dry-run).
        
        Args:
            request: Execution request
            dry_run: Override flag
            
        Returns:
            True if should execute, False if dry-run
        """
        if dry_run is not None:
            return not dry_run
        if request.dry_run is not None:
            return not request.dry_run
        return not self.dry_run


class ChannelRegistry:
    """
    Registry for execution channels.
    
    Manages channel instances and provides channel lookup.
    """
    
    def __init__(self):
        """Initialize channel registry."""
        self._channels: dict[ChannelType, ExecutionChannel] = {}
    
    def register(self, channel_type: ChannelType, channel: ExecutionChannel) -> None:
        """
        Register a channel implementation.
        
        Args:
            channel_type: Type of channel
            channel: Channel instance
        """
        self._channels[channel_type] = channel
    
    def get_channel(self, channel_type: ChannelType) -> Optional[ExecutionChannel]:
        """
        Get channel by type.
        
        Args:
            channel_type: Type of channel
            
        Returns:
            Channel instance or None if not registered
        """
        return self._channels.get(channel_type)
    
    def has_channel(self, channel_type: ChannelType) -> bool:
        """
        Check if channel is registered.
        
        Args:
            channel_type: Type of channel
            
        Returns:
            True if channel is registered
        """
        return channel_type in self._channels


# Global channel registry
_channel_registry = ChannelRegistry()


def get_channel_registry() -> ChannelRegistry:
    """
    Get global channel registry.
    
    Returns:
        ChannelRegistry instance
    """
    return _channel_registry


def register_channel(channel_type: ChannelType, channel: ExecutionChannel) -> None:
    """
    Register a channel in the global registry.
    
    Args:
        channel_type: Type of channel
        channel: Channel instance
    """
    _channel_registry.register(channel_type, channel)
