from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseTool(ABC):
    def __init__(self, name: str, description: str, parameters_schema: Optional[Dict[str, Any]] = None):
        self.name = name
        self.description = description
        self.parameters_schema = parameters_schema or {}

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        pass
