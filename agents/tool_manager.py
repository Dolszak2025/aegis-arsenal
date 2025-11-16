from typing import Any, Dict, List
from abc import ABC, abstractmethod
import uuid
import logging

logger = logging.getLogger("agents.tool_manager")


from .base_tool import BaseTool


from .google_drawings_tool import GoogleDrawingsTool


# Słownik dostępnych narzędzi
AVAILABLE_TOOLS: Dict[str, BaseTool] = {
    "google-drawings-tool": GoogleDrawingsTool(),  # -> rejestruje tworzenie diagramów
}

__all__ = ["BaseTool", "GoogleDrawingsTool", "AVAILABLE_TOOLS"]
