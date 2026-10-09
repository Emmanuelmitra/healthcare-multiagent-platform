from ..core.base_agent import BaseAgent
from ..core.registry import AgentRegistry

@AgentRegistry.register("supervisor_agent")
class SupervisorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SupervisorAgent",
            role_description="Decomposes clinical requests and coordinates sub-agents.",
            system_instruction="You are the Lead Clinical Orchestrator Agent. Analyze queries and formulate a multi-agent plan."
        )
