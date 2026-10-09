import unittest
from src.tools.patient_records import patient_records_tool
from src.tools.clinical_guidelines import clinical_guidelines_tool
from src.tools.drug_interactions import drug_interactions_tool

class TestTools(unittest.TestCase):
    def test_patient_records_tool(self):
        res = patient_records_tool.execute(patient_id="PT-1001")
        self.assertEqual(res["status"], "found")
        self.assertIn("Hypertension", res["patient"]["conditions"])

    def test_clinical_guidelines_tool(self):
        res = clinical_guidelines_tool.execute(query="chest pain", top_k=2)
        self.assertGreater(res["total_found"], 0)

    def test_drug_interactions_tool(self):
        res = drug_interactions_tool.execute(medications=["Lisinopril 10mg", "Spironolactone 25mg"])
        self.assertTrue(res["has_interactions"])

if __name__ == "__main__":
    unittest.main()
