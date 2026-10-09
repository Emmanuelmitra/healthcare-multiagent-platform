from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from .config import settings
from .workflows.healthcare_flow import healthcare_workflow
from .memory.session_memory import session_memory
from .observability.tracker import tracker
from .core.registry import AgentRegistry, ToolRegistry
from .tools.patient_records import patient_records_tool
from .tools.clinical_guidelines import clinical_guidelines_tool
from .tools.drug_interactions import drug_interactions_tool

app = FastAPI(
    title=settings.app_name,
    description="Production Multi-Agent AI Platform for Healthcare & General Domains",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    query: str = Field(..., description="User medical query or symptoms", example="Patient reports acute chest pain radiating to left arm.")
    patient_id: Optional[str] = Field(None, description="Optional Patient ID for EHR retrieval", example="PT-1001")
    session_id: Optional[str] = Field(None, description="Optional Session ID for multi-turn conversations")

class ApprovalRequest(BaseModel):
    session_id: str
    approved: bool
    clinician_notes: Optional[str] = None

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "environment": settings.app_env,
        "memory_backend": settings.memory_backend
    }

@app.get("/api/v1/agents")
def list_registered_agents():
    return {"registered_agents": list(AgentRegistry.list_agents().keys())}

@app.get("/api/v1/tools")
def list_registered_tools():
    return {"registered_tools": list(ToolRegistry.list_tools().keys())}

@app.get("/api/v1/telemetry")
def get_telemetry():
    return tracker.get_summary()

@app.post("/api/v1/chat")
def process_chat(req: ChatRequest):
    try:
        state = healthcare_workflow.run(
            user_query=req.query,
            patient_id=req.patient_id,
            session_id=req.session_id
        )
        return {
            "session_id": state.session_id,
            "final_response": state.final_response,
            "needs_human_approval": state.needs_human_approval,
            "human_approval_reason": state.human_approval_reason,
            "guardrail_flags": state.guardrail_flags,
            "messages_count": len(state.messages),
            "audit_trail_count": len(state.audit_log)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/session/{session_id}")
def get_session(session_id: str):
    state = session_memory.get_state(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    return state.to_dict()

@app.post("/api/v1/human-approval")
def submit_human_approval(req: ApprovalRequest):
    state = session_memory.get_state(req.session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    state.record_audit(
        action="clinician_approval_recorded",
        agent="HumanClinician",
        details={"approved": req.approved, "notes": req.clinician_notes}
    )
    if req.approved:
        state.needs_human_approval = False
        state.final_response = f"[Clinician Approved]: {state.final_response}"
    else:
        state.final_response = f"[Clinician Rejected]: Notes: {req.clinician_notes}"
    session_memory.save_state(state)
    return {"status": "success", "session_id": req.session_id, "approved": req.approved}
