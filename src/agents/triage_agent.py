from ..core.base_agent import BaseAgent
from ..core.state import ExecutionState
from ..core.registry import AgentRegistry
from ..tools.patient_records import patient_records_tool

@AgentRegistry.register("triage_agent")
class TriageAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="TriageAgent",
            role_description="Performs intake and symptom triage.",
            system_instruction="You are an expert Triage AI Agent. Classify symptom urgency and extract clinical context.",
            tools=[patient_records_tool]
        )

    def on_start(self, state: ExecutionState) -> None:
        if state.patient_id and "patient_record" not in state.context:
            res = patient_records_tool.execute(patient_id=state.patient_id)
            if res.get("status") == "found":
                state.context["patient_record"] = res["patient"]
