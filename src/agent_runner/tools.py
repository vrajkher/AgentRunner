from abc import ABC, abstractmethod
from typing import Any, Callable


class ToolAdapter(ABC):
    name: str

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        raise NotImplementedError


class FunctionTool(ToolAdapter):
    def __init__(self, name: str, fn: Callable[..., Any]):
        self.name = name
        self.fn = fn

    def execute(self, **kwargs: Any) -> Any:
        return self.fn(**kwargs)


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolAdapter] = {}

    def register(self, tool: ToolAdapter) -> None:
        if not getattr(tool, "name", None):
            raise ValueError("Tool must have a non-empty name")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolAdapter:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def list(self) -> list[str]:
        return sorted(self._tools)
