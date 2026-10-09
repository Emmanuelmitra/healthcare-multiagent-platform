from abc import ABC
from typing import List, Dict, Any, Optional
import time
import logging

from .state import ExecutionState, AgentMessage, Role
from .llm_client import GoogleGenAIClient, llm_client
from ..config import settings

logger = logging.getLogger("BaseAgent")

class BaseAgent(ABC):
    def __init__(
        self,
        name: str,
        role_description: str,
        system_instruction: str,
        model: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        client: Optional[GoogleGenAIClient] = None
    ):
        self.name = name
        self.role_description = role_description
        self.system_instruction = system_instruction
        self.model = model or settings.gemini_model
        self.tools = tools or []
        self.client = client or llm_client

    def run(self, state: ExecutionState) -> ExecutionState:
        start_time = time.time()
        state.current_agent = self.name
        self.on_start(state)

        formatted_messages = self._build_prompt_context(state)
        response = self.client.generate(
            system_instruction=self.system_instruction,
            messages=formatted_messages,
            model=self.model,
            tools=self.tools
        )

        tool_results = []
        if response.tool_calls:
            tool_results = self._execute_tools(response.tool_calls, state)

        agent_message = AgentMessage(
            role=Role.AGENT,
            sender=self.name,
            content=response.content,
            tool_calls=response.tool_calls,
            tool_results=tool_results,
            metadata={
                "tokens": response.total_tokens,
                "latency_sec": response.latency_sec,
                "model": response.model_name
            }
        )
        state.add_message(agent_message)

        elapsed = round(time.time() - start_time, 3)
        state.record_audit(
            action="agent_execution_completed",
            agent=self.name,
            details={"latency_sec": elapsed, "tokens": response.total_tokens}
        )
        self.on_finish(state, agent_message)
        return state

    def _build_prompt_context(self, state: ExecutionState) -> List[Dict[str, str]]:
        context = []
        for msg in state.messages[-6:]:
            context.append({
                "role": "user" if msg.role == Role.USER else "assistant",
                "content": f"[{msg.sender}]: {msg.content}"
            })
        if not context:
            context.append({"role": "user", "content": state.user_query})
        return context

    def _execute_tools(self, tool_calls: List[Dict[str, Any]], state: ExecutionState) -> List[Dict[str, Any]]:
        results = []
        for call in tool_calls:
            name = call.get("name")
            args = call.get("args", {})
            matched = next((t for t in self.tools if getattr(t, "name", None) == name), None)
            if matched:
                try:
                    res = matched.execute(**args)
                    results.append({"tool": name, "status": "success", "result": res})
                except Exception as e:
                    results.append({"tool": name, "status": "error", "error": str(e)})
        return results

    def on_start(self, state: ExecutionState) -> None:
        pass

    def on_finish(self, state: ExecutionState, message: AgentMessage) -> None:
        pass
