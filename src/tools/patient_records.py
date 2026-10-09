from typing import Dict, Any
from .base import BaseTool

class PatientRecordsTool(BaseTool):
    SYNTHETIC_EHR_DB = {
        "PT-1001": {
            "patient_id": "PT-1001",
            "age": 58,
            "conditions": ["Hypertension", "Type 2 Diabetes Mellitus"],
            "active_medications": ["Metformin 1000mg BID", "Lisinopril 20mg Daily"],
            "allergies": ["Penicillin"]
        }
    }
    def __init__(self):
        super().__init__(name="get_patient_ehr", description="Retrieves patient EHR summary.")

    def execute(self, patient_id: str) -> Dict[str, Any]:
        patient = self.SYNTHETIC_EHR_DB.get(patient_id.upper())
        if not patient:
            return {"status": "not_found", "patient_id": patient_id}
        return {"status": "found", "patient": patient}

patient_records_tool = PatientRecordsTool()
