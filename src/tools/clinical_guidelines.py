from typing import Dict, Any
from .base import BaseTool
from ..core.registry import ToolRegistry
from ..memory.vector_memory import vector_memory


@ToolRegistry.register("search_clinical_guidelines")
class ClinicalGuidelinesTool(BaseTool):

    def __init__(self):
        super().__init__(
            name="search_clinical_guidelines",
            description="Searches institutional clinical protocols and treatment pathways.",
        )

    def execute(self, query: str, top_k: int = 2) -> Dict[str, Any]:
        results = vector_memory.search(query=query, top_k=top_k)
        return {
            "query": query,
            "matched_guidelines": results,
            "total_found": len(results),
        }


clinical_guidelines_tool = ClinicalGuidelinesTool()
