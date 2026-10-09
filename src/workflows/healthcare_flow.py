from typing import Optional
import time
from ..core.state import ExecutionState, AgentMessage, Role
from ..guardrails.phi_scrubber import phi_scrubber
from ..guardrails.prompt_guard import prompt_guard
from ..observability.tracker import tracker
from ..memory.session_memory import session_memory
from ..config import settings
from ..agents.supervisor import SupervisorAgent
from ..agents.triage_agent import TriageAgent
from ..agents.diagnostic_agent import DiagnosticAgent
from ..agents.compliance_agent import ComplianceAgent

class HealthcareWorkflow:
    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.triage = TriageAgent()
        self.diagnostic = DiagnosticAgent()
        self.compliance = ComplianceAgent()

    def run(self, user_query: str, patient_id: Optional[str] = None, session_id: Optional[str] = None) -> ExecutionState:
        start_time = time.time()
        if session_id:
            existing = session_memory.get_state(session_id)
            state = existing or ExecutionState(session_id=session_id, patient_id=patient_id, user_query=user_query)
        else:
            state = ExecutionState(patient_id=patient_id, user_query=user_query)

        # 1. Prompt Guard
        if settings.enable_prompt_guard:
            is_safe, guard_meta = prompt_guard.validate(user_query)
            state.add_guardrail_flag("PromptGuard", is_safe, guard_meta)
            if not is_safe:
                state.is_completed = True
                state.final_response = "Security Warning: Input violated safety policy (adversarial pattern detected)."
                session_memory.save_state(state)
                return state

        # 2. PHI Scrubber
        sanitized_query = user_query
        if settings.enable_phi_scrubbing:
            sanitized_query, phi_meta = phi_scrubber.sanitize(user_query)
            state.add_guardrail_flag("PHIScrubber", not phi_meta["scrubbed"], phi_meta)

        state.add_message(AgentMessage(role=Role.USER, sender="User", content=sanitized_query))

        # 3. Agent Execution Chain
        state = self.supervisor.run(state)
        state = self.triage.run(state)
        state = self.diagnostic.run(state)
        state = self.compliance.run(state)

        elapsed = round(time.time() - start_time, 3)
        total_tokens = sum(m.metadata.get("tokens", 0) for m in state.messages if m.metadata)
        tracker.record_usage(
            session_id=state.session_id,
            agent_name="HealthcareWorkflow",
            prompt_tokens=int(total_tokens * 0.4),
            completion_tokens=int(total_tokens * 0.6),
            latency_sec=elapsed
        )
        session_memory.save_state(state)
        return state

healthcare_workflow = HealthcareWorkflow()
