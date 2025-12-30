from typing import Any, Dict
from abc import ABC, abstractmethod


class BaseTool(ABC):
    """Prosta klasa bazowa narzędzi. Możesz rozszerzyć ją w projekcie."""

    name: str = "base_tool"
    description: str = "Base tool"

    @abstractmethod
    def get_function_definition(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError
