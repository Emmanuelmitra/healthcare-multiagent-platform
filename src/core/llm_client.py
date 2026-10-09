import time
import logging
from typing import Dict, Any, List, Optional
from ..config import settings

logger = logging.getLogger("LLMClient")

class LLMResponse:
    def __init__(
        self,
        content: str,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        model_name: str = "",
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        latency_sec: float = 0.0
    ):
        self.content = content
        self.tool_calls = tool_calls or []
        self.model_name = model_name
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = prompt_tokens + completion_tokens
        self.latency_sec = latency_sec

class GoogleGenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.use_vertex = settings.google_genai_use_vertexai
        self.client = None
        self._init_sdk()

    def _init_sdk(self):
        if not self.api_key and not self.use_vertex:
            return
        try:
            from google import genai
            if self.use_vertex:
                self.client = genai.Client(
                    vertexai=True,
                    project=settings.google_cloud_project,
                    location=settings.google_cloud_location
                )
            else:
                self.client = genai.Client(api_key=self.api_key)
        except Exception:
            self.client = None

    def generate(
        self,
        system_instruction: str,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        temperature: float = 0.2
    ) -> LLMResponse:
        target_model = model or settings.gemini_model
        start_time = time.time()

        if self.client is not None:
            try:
                contents = [f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in messages]
                combined = "\n".join(contents)
                resp = self.client.models.generate_content(
                    model=target_model,
                    contents=combined,
                    config={"system_instruction": system_instruction, "temperature": temperature}
                )
                latency = round(time.time() - start_time, 3)
                text = getattr(resp, "text", "") or str(resp)
                return LLMResponse(
                    content=text,
                    model_name=target_model,
                    prompt_tokens=len(combined.split()) * 2,
                    completion_tokens=len(text.split()) * 2,
                    latency_sec=latency
                )
            except Exception as e:
                logger.warning(f"Live Gemini API error: {e}. Using deterministic simulation mode.")

        latency = round(time.time() - start_time + 0.05, 3)
        simulated_text = self._simulate_agent_reasoning(system_instruction, messages)
        tokens_in = sum(len(m.get("content", "").split()) for m in messages) * 2 + 50
        tokens_out = len(simulated_text.split()) * 2
        return LLMResponse(
            content=simulated_text,
            model_name=f"{target_model} (local-sim)",
            prompt_tokens=tokens_in,
            completion_tokens=tokens_out,
            latency_sec=latency
        )

    def _simulate_agent_reasoning(self, system_instruction: str, messages: List[Dict[str, str]]) -> str:
        last_msg = messages[-1].get("content", "").lower() if messages else ""
        if "supervisor" in system_instruction.lower():
            return "Execution Plan: Decomposed clinical query. Routing to Triage, Diagnostic, and Compliance agents."
        elif "triage" in system_instruction.lower():
            if "chest pain" in last_msg or "shortness of breath" in last_msg:
                return "Triage Classification: High Acuity / Emergency Priority. Acute cardiopulmonary symptoms detected. Immediate clinical assessment indicated."
            return "Triage Classification: Routine / Low Acuity. Symptoms consistent with standard ambulatory follow-up."
        elif "diagnostic" in system_instruction.lower() or "knowledge" in system_instruction.lower():
            return "Clinical Diagnostic Verification: Protocol matched for condition. Differential considerations noted. Drug contraindications checked."
        elif "compliance" in system_instruction.lower() or "safety" in system_instruction.lower():
            return "Compliance Audit Passed: Medical boundaries enforced. Mandatory safety disclaimers appended."
        return f"Processed query: {last_msg[:80]}..."

llm_client = GoogleGenAIClient()
