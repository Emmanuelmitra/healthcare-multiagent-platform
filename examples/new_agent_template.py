import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.base_agent import BaseAgent
from src.core.state import ExecutionState
from src.core.registry import AgentRegistry

@AgentRegistry.register("custom_domain_agent")
class CustomDomainAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CustomDomainAgent",
            role_description="Example agent for any new domain (Finance, E-Commerce, Legal)",
            system_instruction="You are an expert domain agent. Execute tasks with high rigor."
        )

if __name__ == "__main__":
    agent = CustomDomainAgent()
    state = ExecutionState(user_query="Analyze quarterly performance metrics.")
    state = agent.run(state)
    print(f"Agent {agent.name} Output: {state.messages[-1].content}")
