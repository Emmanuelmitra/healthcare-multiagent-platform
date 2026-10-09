"""FastAPI Application Server with Embedded Web UI for Multi-Agent Healthcare Platform."""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .agents.compliance_agent import ComplianceAgent
from .agents.diagnostic_agent import DiagnosticAgent
from .agents.supervisor import SupervisorAgent
from .agents.triage_agent import TriageAgent
from .config import settings
from .core.registry import AgentRegistry, ToolRegistry
from .memory.session_memory import session_memory
from .observability.tracker import tracker
from .tools.clinical_guidelines import clinical_guidelines_tool
from .tools.drug_interactions import drug_interactions_tool
from .tools.patient_records import patient_records_tool
from .workflows.healthcare_flow import healthcare_workflow

app = FastAPI(
    title=settings.app_name,
    description="Production Multi-Agent AI Platform for Healthcare & General Domains",
    version="1.0.0",
)


class ChatRequest(BaseModel):
  query: str = Field(..., description="User medical query or symptoms")
  patient_id: Optional[str] = Field(None, description="Patient ID")
  session_id: Optional[str] = Field(None, description="Session ID")


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
        session_id=req.session_id,
    )
    return {
        "session_id": state.session_id,
        "final_response": state.final_response,
        "needs_human_approval": state.needs_human_approval,
        "human_approval_reason": state.human_approval_reason,
        "guardrail_flags": state.guardrail_flags,
        "messages": [m.to_dict() for m in state.messages],
        "audit_trail_count": len(state.audit_log),
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
      details={"approved": req.approved, "notes": req.clinician_notes},
  )
  if req.approved:
    state.needs_human_approval = False
    state.final_response = f"[Clinician Approved]: {state.final_response}"
  else:
    state.final_response = (
        f"[Clinician Rejected]: Order rejected. Notes: {req.clinician_notes}"
    )
  session_memory.save_state(state)
  return {
      "status": "success",
      "session_id": req.session_id,
      "approved": req.approved,
      "updated_response": state.final_response,
  }


# Embedded Clean Modern Frontend UI
@app.get("/", response_class=HTMLResponse)
def serve_ui():
  return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HealthAgent AI | Enterprise Multi-Agent Clinical Platform</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .chat-scroll::-webkit-scrollbar { width: 6px; }
        .chat-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 font-sans antialiased h-screen flex flex-col">

    <!-- Top Header -->
    <header class="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between shadow-sm flex-shrink-0">
        <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white text-xl shadow-md shadow-blue-500/20">
                <i class="fa-solid fa-hospital-user"></i>
            </div>
            <div>
                <h1 class="font-bold text-lg text-slate-900 leading-tight">HealthAgent AI</h1>
                <p class="text-xs text-slate-500">Autonomous Multi-Agent Clinical Decision Support (Google ADK)</p>
            </div>
        </div>
        <div class="flex items-center space-x-4">
            <div class="hidden sm:flex items-center space-x-2 text-xs bg-slate-100 text-slate-700 px-3 py-1.5 rounded-full border border-slate-200">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>Active Pipeline: <b>4 Agents</b></span>
            </div>
            <a href="/docs" target="_blank" class="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center space-x-1">
                <i class="fa-solid fa-code"></i>
                <span>API Docs</span>
            </a>
        </div>
    </header>

    <!-- Main Container -->
    <div class="flex-1 flex overflow-hidden max-w-7xl w-full mx-auto p-4 gap-4">

        <!-- Left Column: Controls & Agent Status -->
        <aside class="w-80 flex-shrink-0 flex flex-col gap-4">
            
            <!-- Patient Selector Card -->
            <div class="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm">
                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                    <i class="fa-solid fa-id-card-clip mr-1 text-blue-500"></i> Active Patient Record
                </label>
                <select id="patientSelect" class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-sm font-medium focus:ring-2 focus:ring-blue-500 focus:outline-none">
                    <option value="">None (General Inquiry)</option>
                    <option value="PT-1001" selected>PT-1001 (58F, Diabetes, Hypertension)</option>
                    <option value="PT-1002">PT-1002 (42M, Mild Asthma, Hyperlipidemia)</option>
                </select>
                <div id="patientDetails" class="mt-3 text-xs text-slate-600 bg-slate-50 rounded-xl p-2.5 border border-slate-100">
                    <p><b>Allergies:</b> Penicillin (Anaphylaxis)</p>
                    <p class="mt-1"><b>Meds:</b> Metformin 1000mg BID, Lisinopril 20mg</p>
                </div>
            </div>

            <!-- Pipeline Visualizer Card -->
            <div class="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm flex-1 flex flex-col">
                <h3 class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
                    <i class="fa-solid fa-network-wired mr-1 text-indigo-500"></i> Orchestrated Agents
                </h3>
                <div class="space-y-2 text-xs flex-1">
                    <div id="step-supervisor" class="p-2.5 rounded-xl border border-slate-100 bg-slate-50 flex items-center justify-between">
                        <div class="flex items-center space-x-2">
                            <i class="fa-solid fa-sitemap text-blue-600"></i>
                            <span class="font-medium text-slate-700">Supervisor</span>
                        </div>
                        <span class="status-badge text-[10px] text-slate-400">Idle</span>
                    </div>
                    <div id="step-triage" class="p-2.5 rounded-xl border border-slate-100 bg-slate-50 flex items-center justify-between">
                        <div class="flex items-center space-x-2">
                            <i class="fa-solid fa-stethoscope text-amber-600"></i>
                            <span class="font-medium text-slate-700">Triage Specialist</span>
                        </div>
                        <span class="status-badge text-[10px] text-slate-400">Idle</span>
                    </div>
                    <div id="step-diagnostic" class="p-2.5 rounded-xl border border-slate-100 bg-slate-50 flex items-center justify-between">
                        <div class="flex items-center space-x-2">
                            <i class="fa-solid fa-book-medical text-purple-600"></i>
                            <span class="font-medium text-slate-700">Clinical Protocols</span>
                        </div>
                        <span class="status-badge text-[10px] text-slate-400">Idle</span>
                    </div>
                    <div id="step-compliance" class="p-2.5 rounded-xl border border-slate-100 bg-slate-50 flex items-center justify-between">
                        <div class="flex items-center space-x-2">
                            <i class="fa-solid fa-shield-halved text-emerald-600"></i>
                            <span class="font-medium text-slate-700">Safety & Compliance</span>
                        </div>
                        <span class="status-badge text-[10px] text-slate-400">Idle</span>
                    </div>
                </div>

                <!-- Telemetry Card -->
                <div class="mt-4 pt-4 border-t border-slate-100 text-xs text-slate-500 flex justify-between items-center">
                    <span>Est. Cost: <b id="costDisplay" class="text-slate-800">$0.0000</b></span>
                    <span>Tokens: <b id="tokenDisplay" class="text-slate-800">0</b></span>
                </div>
            </div>
        </aside>

        <!-- Right Column: Interactive Chat & Reasoning Feed -->
        <main class="flex-1 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col overflow-hidden">
            
            <!-- Quick Example Chips -->
            <div class="p-3 bg-slate-50 border-b border-slate-200 flex items-center gap-2 overflow-x-auto text-xs flex-shrink-0">
                <span class="text-slate-400 font-medium whitespace-nowrap"><i class="fa-regular fa-lightbulb mr-1"></i>Try:</span>
                <button onclick="setQuery('Patient reports crushing chest pain radiating to left jaw, onset 25 mins ago.')" 
                    class="px-2.5 py-1 bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200 rounded-lg whitespace-nowrap transition">
                    🚨 Severe Chest Pain (Triggers Approval)
                </button>
                <button onclick="setQuery('Patient asking for routine glycemic control guidance and HbA1c target.')" 
                    class="px-2.5 py-1 bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 rounded-lg whitespace-nowrap transition">
                    📋 Diabetes Protocol
                </button>
                <button onclick="setQuery('Patient SSN 123-45-6789 and phone 555-019-2834 needs follow-up.')" 
                    class="px-2.5 py-1 bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 rounded-lg whitespace-nowrap transition">
                    🔒 Test HIPAA PHI Redaction
                </button>
            </div>

            <!-- Messages Stream Area -->
            <div id="chatMessages" class="flex-1 overflow-y-auto p-4 space-y-4 chat-scroll">
                <div class="flex items-start space-x-3 text-sm">
                    <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold flex-shrink-0">
                        <i class="fa-solid fa-robot"></i>
                    </div>
                    <div class="bg-slate-100 p-3.5 rounded-2xl rounded-tl-none max-w-xl text-slate-700">
                        Hello! I am your clinical multi-agent assistant. Enter symptoms or select a sample query above. I will automatically orchestrate triage, check guideline protocols, and enforce safety guardrails.
                    </div>
                </div>
            </div>

            <!-- Human Approval Alert Banner (Hidden by default) -->
            <div id="approvalBanner" class="hidden mx-4 mb-2 p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-center justify-between text-xs">
                <div class="flex items-center space-x-2 text-amber-800">
                    <i class="fa-solid fa-triangle-exclamation text-amber-600 text-base"></i>
                    <div>
                        <span class="font-bold">Human Clinician Approval Required:</span>
                        <span id="approvalReasonText">High acuity detected.</span>
                    </div>
                </div>
                <div class="flex items-center space-x-2">
                    <button onclick="submitApproval(true)" class="px-3 py-1.5 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 shadow-sm transition">
                        <i class="fa-solid fa-check mr-1"></i> Approve
                    </button>
                    <button onclick="submitApproval(false)" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg font-medium hover:bg-rose-700 shadow-sm transition">
                        <i class="fa-solid fa-xmark mr-1"></i> Reject
                    </button>
                </div>
            </div>

            <!-- Input Bar -->
            <div class="p-3 border-t border-slate-200 bg-white flex items-center space-x-2 flex-shrink-0">
                <input id="queryInput" type="text" placeholder="Describe symptoms or clinical question..." 
                    class="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    onkeypress="if(event.key === 'Enter') sendQuery()">
                <button id="sendBtn" onclick="sendQuery()" class="px-5 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl text-sm flex items-center space-x-2 shadow-sm shadow-blue-500/20 transition">
                    <span>Send</span>
                    <i class="fa-solid fa-paper-plane text-xs"></i>
                </button>
            </div>
        </main>
    </div>

    <!-- Client Script -->
    <script>
        let currentSessionId = null;

        function setQuery(text) {
            document.getElementById('queryInput').value = text;
        }

        async function sendQuery() {
            const input = document.getElementById('queryInput');
            const query = input.value.trim();
            if (!query) return;

            const patientId = document.getElementById('patientSelect').value;
            input.value = '';
            document.getElementById('approvalBanner').classList.add('hidden');

            appendUserMessage(query);
            setAgentStatus('active');

            try {
                const response = await fetch('/api/v1/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        query: query,
                        patient_id: patientId ? patientId : null,
                        session_id: currentSessionId
                    })
                });

                const data = await response.json();
                currentSessionId = data.session_id;

                appendAgentResponses(data);
                updateTelemetry();

                if (data.needs_human_approval) {
                    document.getElementById('approvalReasonText').innerText = data.human_approval_reason;
                    document.getElementById('approvalBanner').classList.remove('hidden');
                }
            } catch (err) {
                console.error(err);
                appendErrorMessage("Error communicating with multi-agent platform.");
            } finally {
                setAgentStatus('idle');
            }
        }

        function appendUserMessage(text) {
            const container = document.getElementById('chatMessages');
            container.innerHTML += `
                <div class="flex items-start justify-end space-x-3 text-sm">
                    <div class="bg-blue-600 text-white p-3.5 rounded-2xl rounded-tr-none max-w-xl shadow-sm">
                        ${escapeHtml(text)}
                    </div>
                </div>
            `;
            container.scrollTop = container.scrollHeight;
        }

        function appendAgentResponses(data) {
            const container = document.getElementById('chatMessages');
            
            // Render Guardrail flags
            let guardrailBadges = '';
            if (data.guardrail_flags) {
                data.guardrail_flags.forEach(f => {
                    const color = f.passed ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800';
                    guardrailBadges += `<span class="px-2 py-0.5 rounded-md text-[10px] font-semibold ${color} mr-1">${f.guardrail}: ${f.passed ? 'PASS' : 'FLAGGED'}</span>`;
                });
            }

            container.innerHTML += `
                <div class="flex items-start space-x-3 text-sm">
                    <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold flex-shrink-0">
                        <i class="fa-solid fa-user-doctor"></i>
                    </div>
                    <div class="bg-slate-100 border border-slate-200 p-4 rounded-2xl rounded-tl-none max-w-2xl text-slate-800 space-y-3">
                        <div class="flex items-center space-x-1 pb-2 border-b border-slate-200">
                            ${guardrailBadges}
                        </div>
                        <div class="prose prose-sm text-slate-800 whitespace-pre-wrap">${escapeHtml(data.final_response)}</div>
                    </div>
                </div>
            `;
            container.scrollTop = container.scrollHeight;
        }

        async function submitApproval(approved) {
            if (!currentSessionId) return;
            const res = await fetch('/api/v1/human-approval', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    session_id: currentSessionId,
                    approved: approved,
                    clinician_notes: approved ? "Clinician approved via Web UI" : "Rejected by Clinician via Web UI"
                })
            });
            const result = await res.json();
            document.getElementById('approvalBanner').classList.add('hidden');
            
            const container = document.getElementById('chatMessages');
            container.innerHTML += `
                <div class="flex justify-center my-2">
                    <span class="text-xs px-3 py-1 rounded-full font-medium ${approved ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}">
                        ${approved ? '✓ Clinician Approved Order' : '✕ Clinician Rejected Order'}
                    </span>
                </div>
            `;
            container.scrollTop = container.scrollHeight;
        }

        async function updateTelemetry() {
            try {
                const res = await fetch('/api/v1/telemetry');
                const data = await res.json();
                document.getElementById('costDisplay').innerText = '$' + data.total_cost_usd.toFixed(4);
                document.getElementById('tokenDisplay').innerText = data.total_tokens.toLocaleString();
            } catch(e) {}
        }

        function setAgentStatus(status) {
            const steps = ['supervisor', 'triage', 'diagnostic', 'compliance'];
            steps.forEach(s => {
                const badge = document.querySelector(`#step-${s} .status-badge`);
                if (badge) {
                    badge.innerText = status === 'active' ? 'Active' : 'Idle';
                    badge.className = status === 'active' ? 'status-badge text-[10px] text-blue-600 font-bold animate-pulse' : 'status-badge text-[10px] text-slate-400';
                }
            });
        }

        function escapeHtml(text) {
            return text ? text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") : '';
        }
    </script>
</body>
</html>"""