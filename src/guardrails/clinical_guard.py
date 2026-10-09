from typing import Tuple, Dict, Any, List

class ClinicalGuard:
    HIGH_RISK_SYMPTOMS = [
        "severe chest pain",
        "crushing chest pain",
        "loss of consciousness",
        "slurred speech",
        "uncontrolled bleeding",
        "suicidal ideation",
        "anaphylaxis"
    ]
    REQUIRED_DISCLAIMER = (
        "\n\n---\n*Clinical Safety Notice: This AI assessment is for clinical decision-support and informational "
        "purposes only. It is not an official medical diagnosis or prescription. Immediate physician or emergency "
        "medical evaluation is strongly advised for acute, worsening, or severe symptoms.*"
    )

    def evaluate_risk(self, text: str) -> Tuple[float, List[str]]:
        lower = text.lower()
        red_flags = [s for s in self.HIGH_RISK_SYMPTOMS if s in lower]
        risk = 0.9 if red_flags else 0.15
        return risk, red_flags

    def enforce_output_safety(self, response_text: str, risk_score: float) -> str:
        safe_response = response_text
        if risk_score >= 0.7:
            banner = (
                "⚠️ **URGENT MEDICAL NOTICE**: Potential high-acuity condition detected. "
                "If the patient is experiencing a medical emergency, please call 911 / emergency services immediately.\n\n"
            )
            safe_response = banner + safe_response
        if "Clinical Safety Notice:" not in safe_response:
            safe_response = safe_response + self.REQUIRED_DISCLAIMER
        return safe_response

clinical_guard = ClinicalGuard()
