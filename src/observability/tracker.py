from typing import Dict, Any
from datetime import datetime, timezone

class MetricTracker:
    INPUT_COST_PER_M = 0.075
    OUTPUT_COST_PER_M = 0.30

    def __init__(self):
        self.session_metrics: Dict[str, Dict[str, Any]] = {}
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_cost_usd: float = 0.0
        self.total_requests: int = 0

    def record_usage(self, session_id: str, agent_name: str, prompt_tokens: int, completion_tokens: int, latency_sec: float):
        cost = ((prompt_tokens / 1_000_000.0) * self.INPUT_COST_PER_M +
                (completion_tokens / 1_000_000.0) * self.OUTPUT_COST_PER_M)
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_cost_usd += cost
        self.total_requests += 1

        if session_id not in self.session_metrics:
            self.session_metrics[session_id] = {
                "session_id": session_id,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "total_latency_sec": 0.0
            }
        sess = self.session_metrics[session_id]
        sess["total_tokens"] += (prompt_tokens + completion_tokens)
        sess["total_cost_usd"] = round(sess["total_cost_usd"] + cost, 6)
        sess["total_latency_sec"] = round(sess["total_latency_sec"] + latency_sec, 3)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "total_cost_usd": round(self.total_cost_usd, 6),
            "active_sessions": len(self.session_metrics)
        }

tracker = MetricTracker()
