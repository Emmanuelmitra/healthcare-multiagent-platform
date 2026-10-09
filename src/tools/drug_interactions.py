from typing import Dict, Any, List
from .base import BaseTool
from ..core.registry import ToolRegistry


@ToolRegistry.register("check_drug_interactions")
class DrugInteractionsTool(BaseTool):
    KNOWN_INTERACTIONS = [
        ("lisinopril", "spironolactone", "High Risk: Hyperkalemia danger.")
    ]

    def __init__(self):
        super().__init__(
            name="check_drug_interactions",
            description="Checks proposed medications for dangerous clinical interactions.",
        )

    def execute(self, medications: List[str]) -> Dict[str, Any]:
        normalized = [m.lower().split()[0] for m in medications]
        flagged = []
        for d1, d2, warn in self.KNOWN_INTERACTIONS:
            if d1 in normalized and d2 in normalized:
                flagged.append(
                    {"drugs": [d1, d2], "severity": "HIGH", "clinical_warning": warn}
                )
        return {
            "medications_checked": medications,
            "has_interactions": len(flagged) > 0,
            "interactions": flagged,
        }


drug_interactions_tool = DrugInteractionsTool()