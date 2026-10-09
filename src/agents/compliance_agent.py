from ..core.base_agent import BaseAgent
from ..core.state import ExecutionState, AgentMessage
from ..core.registry import AgentRegistry
from ..guardrails.clinical_guard import clinical_guard
from ..config import settings

@AgentRegistry.register("compliance_agent")
class ComplianceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ComplianceAgent",
            role_description="Audits clinical recommendations against safety guardrails.",
            system_instruction="You are a Clinical Safety & Compliance Auditor Agent. Ensure all outputs are verified."
        )

    def on_finish(self, state: ExecutionState, message: AgentMessage) -> None:
        risk_score, red_flags = clinical_guard.evaluate_risk(state.user_query)
        if risk_score >= settings.high_risk_threshold and settings.enable_human_in_the_loop:
            state.needs_human_approval = True
            state.human_approval_reason = f"High-acuity red flag symptoms detected: {', '.join(red_flags)}"
        safe_content = clinical_guard.enforce_output_safety(message.content, risk_score)
        message.content = safe_content
        state.final_response = safe_content
        state.is_completed = True
