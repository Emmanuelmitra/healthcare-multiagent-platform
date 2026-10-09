from typing import Dict, Any, Optional, List
import time
from ..core.state import ExecutionState

class SessionMemory:
    def __init__(self, backend: str = "in_memory"):
        self.backend = backend
        self._local_cache: Dict[str, ExecutionState] = {}
        self._last_accessed: Dict[str, float] = {}

    def save_state(self, state: ExecutionState) -> None:
        self._local_cache[state.session_id] = state
        self._last_accessed[state.session_id] = time.time()

    def get_state(self, session_id: str) -> Optional[ExecutionState]:
        if session_id in self._local_cache:
            self._last_accessed[session_id] = time.time()
            return self._local_cache[session_id]
        return None

    def delete_state(self, session_id: str) -> bool:
        if session_id in self._local_cache:
            del self._local_cache[session_id]
            self._last_accessed.pop(session_id, None)
            return True
        return False

    def list_sessions(self) -> List[str]:
        return list(self._local_cache.keys())

session_memory = SessionMemory()
