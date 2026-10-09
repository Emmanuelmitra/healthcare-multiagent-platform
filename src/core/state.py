from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid

class Role(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    SUPERVISOR = "supervisor"
    TOOL = "tool"

class AgentMessage:
    def __init__(
        self,
        role: Role,
        sender: str,
        content: str,
        timestamp: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tool_results: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.role = role
        self.sender = sender
        self.content = content
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.tool_calls = tool_calls or []
        self.tool_results = tool_results or []
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value if isinstance(self.role, Role) else self.role,
            "sender": self.sender,
            "content": self.content,
            "timestamp": self.timestamp,
            "tool_calls": self.tool_calls,
            "tool_results": self.tool_results,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        return cls(
            role=Role(data.get("role", "agent")),
            sender=data.get("sender", "unknown"),
            content=data.get("content", ""),
            timestamp=data.get("timestamp"),
            tool_calls=data.get("tool_calls", []),
            tool_results=data.get("tool_results", []),
            metadata=data.get("metadata", {})
        )

class ExecutionState:
    def __init__(
        self,
        session_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        user_query: str = "",
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.session_id = session_id or str(uuid.uuid4())
        self.patient_id = patient_id
        self.user_query = user_query
        self.current_agent: Optional[str] = None
        self.messages: List[AgentMessage] = []
        self.context: Dict[str, Any] = context or {}
        self.guardrail_flags: List[Dict[str, Any]] = []
        self.audit_log: List[Dict[str, Any]] = []
        self.is_completed: bool = False
        self.needs_human_approval: bool = False
        self.human_approval_reason: Optional[str] = None
        self.final_response: Optional[str] = None
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at
        self.metadata: Dict[str, Any] = metadata or {}

    def add_message(self, message: AgentMessage) -> None:
        self.messages.append(message)
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def record_audit(self, action: str, agent: str, details: Dict[str, Any]) -> None:
        self.audit_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "agent": agent,
            "details": details
        })
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def add_guardrail_flag(self, guardrail_name: str, passed: bool, details: Dict[str, Any]) -> None:
        self.guardrail_flags.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "guardrail": guardrail_name,
            "passed": passed,
            "details": details
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "patient_id": self.patient_id,
            "user_query": self.user_query,
            "current_agent": self.current_agent,
            "messages": [m.to_dict() for m in self.messages],
            "context": self.context,
            "guardrail_flags": self.guardrail_flags,
            "audit_log": self.audit_log,
            "is_completed": self.is_completed,
            "needs_human_approval": self.needs_human_approval,
            "human_approval_reason": self.human_approval_reason,
            "final_response": self.final_response,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }
