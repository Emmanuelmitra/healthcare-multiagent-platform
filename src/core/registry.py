from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("Registry")

class AgentRegistry:
    _registry: Dict[str, Any] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(subclass):
            cls._registry[name.lower()] = subclass
            return subclass
        return decorator

    @classmethod
    def get(cls, name: str) -> Optional[Any]:
        return cls._registry.get(name.lower())

    @classmethod
    def list_agents(cls) -> Dict[str, Any]:
        return dict(cls._registry)

class ToolRegistry:
    _registry: Dict[str, Any] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(tool):
            cls._registry[name.lower()] = tool
            return tool
        return decorator

    @classmethod
    def get(cls, name: str) -> Optional[Any]:
        return cls._registry.get(name.lower())

    @classmethod
    def list_tools(cls) -> Dict[str, Any]:
        return dict(cls._registry)
