from typing import List, Dict, Any, Optional
import math
import re

class MemoryRecord:
    def __init__(self, record_id: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.record_id = record_id
        self.content = content
        self.metadata = metadata or {}
        self.tokens = self._tokenize(content)

    @staticmethod
    def _tokenize(text: str) -> Dict[str, int]:
        words = re.findall(r"\b\w+\b", text.lower())
        counts: Dict[str, int] = {}
        for w in words:
            counts[w] = counts.get(w, 0) + 1
        return counts

class VectorMemory:
    def __init__(self):
        self.records: List[MemoryRecord] = []
        self._seed_default_knowledge()

    def _seed_default_knowledge(self):
        protocols = [
            ("CP-001", "Acute Chest Pain Protocol: Obtain 12-lead ECG within 10 minutes. High sensitivity troponin assay. Contraindication: Nitrates contraindicated in hypotension.", {"category": "cardiology", "acuity": "emergency"}),
            ("CP-002", "Type 2 Diabetes Glycemic Protocol: First-line pharmacological therapy is Metformin unless eGFR < 30 mL/min/1.73m2.", {"category": "endocrinology", "acuity": "chronic"}),
            ("CP-003", "Adult Asthma Exacerbation: Assess peak flow. Administer Albuterol SABA via nebulizer with systemic corticosteroids.", {"category": "pulmonology", "acuity": "urgent"}),
        ]
        for rid, text, meta in protocols:
            self.add(rid, text, meta)

    def add(self, record_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.records.append(MemoryRecord(record_id, content, metadata))

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_tokens = MemoryRecord._tokenize(query)
        if not query_tokens:
            return []
        scored = []
        for rec in self.records:
            score = self._compute_similarity(query_tokens, rec.tokens)
            if score > 0.05:
                scored.append((score, rec))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "record_id": rec.record_id,
                "content": rec.content,
                "metadata": rec.metadata,
                "similarity_score": round(score, 3)
            }
            for score, rec in scored[:top_k]
        ]

    def _compute_similarity(self, q_tokens: Dict[str, int], doc_tokens: Dict[str, int]) -> float:
        intersection = set(q_tokens.keys()) & set(doc_tokens.keys())
        if not intersection:
            return 0.0
        dot_product = sum(q_tokens[w] * doc_tokens[w] for w in intersection)
        mag_q = math.sqrt(sum(v ** 2 for v in q_tokens.values()))
        mag_doc = math.sqrt(sum(v ** 2 for v in doc_tokens.values()))
        if mag_q == 0 or mag_doc == 0:
            return 0.0
        return dot_product / (mag_q * mag_doc)

vector_memory = VectorMemory()
