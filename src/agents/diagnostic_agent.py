from ..core.base_agent import BaseAgent
from ..core.state import ExecutionState
from ..core.registry import AgentRegistry
from ..tools.clinical_guidelines import clinical_guidelines_tool

@AgentRegistry.register("diagnostic_agent")
class DiagnosticAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="DiagnosticAgent",
            role_description="Cross-references clinical guidelines.",
            system_instruction="You are a Clinical Protocol AI Agent. Verify guidelines and differential considerations.",
            tools=[clinical_guidelines_tool]
        )
