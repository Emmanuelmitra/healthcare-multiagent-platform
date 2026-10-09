import re
from typing import Tuple, Dict, Any

class PromptGuard:
    INJECTION_SIGNATURES = [
        r"ignore (all )?(previous|prior) (instructions|directions|rules)",
        r"disregard (all )?(prior|system) (prompts|rules)",
        r"reveal your (system prompt|internal instructions|hidden rules)",
        r"output the exact (system|developer) (message|instructions)"
    ]

    def validate(self, text: str) -> Tuple[bool, Dict[str, Any]]:
        lower = text.lower()
        matched = [sig for sig in self.INJECTION_SIGNATURES if re.search(sig, lower)]
        is_safe = len(matched) == 0
        return is_safe, {
            "passed": is_safe,
            "threat_category": "PROMPT_INJECTION" if not is_safe else "NONE",
            "matched_signatures": matched
        }

prompt_guard = PromptGuard()
