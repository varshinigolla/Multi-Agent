from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

class AgentStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"
    WAITING = "waiting"

@dataclass
class AgentResult:
    agent_id: str
    status: AgentStatus
    data: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

class BaseAgent(ABC):
    def __init__(self, agent_id: str, role: str, description: str):
        self.agent_id = agent_id
        self.role = role
        self.description = description
        self.status = AgentStatus.IDLE
        self.context = {}
        self.results = []
        self.logger = logging.getLogger(f"Agent.{agent_id}")
        
    def update_status(self, status: AgentStatus):
        """Update agent status and log the change"""
        self.status = status
        self.logger.info(f"Status changed to {status.value}")
        
    def add_to_context(self, key: str, value: Any):
        """Add data to agent context for sharing with other agents"""
        self.context[key] = value
        self.logger.debug(f"Added to context: {key}")
        
    def get_from_context(self, key: str, default: Any = None):
        """Retrieve data from agent context"""
        return self.context.get(key, default)
        
    def store_result(self, data: Any, metadata: Dict[str, Any] = None):
        """Store agent execution result"""
        result = AgentResult(
            agent_id=self.agent_id,
            status=self.status,
            data=data,
            metadata=metadata or {}
        )
        self.results.append(result)
        self.logger.info(f"Stored result with {len(str(data))} characters of data")
        
    @abstractmethod
    async def execute(self, task: str, context: Dict[str, Any] = None) -> AgentResult:
        """Execute the agent's specific task"""
        pass
        
    def can_handle(self, task: str) -> bool:
        """Determine if this agent can handle the given task"""
        return True
        
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return [self.role]
        
    def __str__(self):
        return f"{self.agent_id} ({self.role}): {self.description}"
