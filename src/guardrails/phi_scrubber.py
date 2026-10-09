import re
from typing import Tuple, Dict, Any, List

class PHIScrubber:
    PATTERNS = {
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b",
        "MRN": r"\b(MRN|mrn|Medical Record #?)\s*[:#]?\s*([A-Za-z0-9]{6,10})\b",
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "PHONE": r"\b(\+?1[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b"
    }

    def sanitize(self, text: str) -> Tuple[str, Dict[str, Any]]:
        redacted = text
        detections = []
        for phi_type, pat in self.PATTERNS.items():
            matches = list(re.finditer(pat, redacted, re.IGNORECASE))
            if matches:
                for m in matches:
                    detections.append({"type": phi_type, "span": f"[{m.start()}:{m.end()}]"})
                redacted = re.sub(pat, f"[REDACTED_{phi_type}]", redacted, flags=re.IGNORECASE)
        return redacted, {"scrubbed": len(detections) > 0, "detections_count": len(detections)}

phi_scrubber = PHIScrubber()
