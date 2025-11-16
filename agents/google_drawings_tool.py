from typing import Any, Dict, List
from abc import abstractmethod
import uuid
import logging

from .base_tool import BaseTool

logger = logging.getLogger("agents.google_drawings_tool")


class GoogleDrawingsTool(BaseTool):
    """Tworzy rysunki/diagramy (Google Drawings) - symulacja."""

    name = "create_drawing"
    description = (
        "Tworzy rysunki/diagramy (Google Drawings) - symulacja. "
        "Przydatne do dokumentacji technicznej."
    )

    def get_function_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "elements": {"type": "array"},
                    "folder_path": {"type": "string"},
                },
                "required": ["title", "elements", "folder_path"],
            },
        }

    def execute(self, title: str, elements: List[Dict[str, Any]], folder_path: str, style_template: str = "Standard Diagram") -> Dict[str, Any]:
        drawing_id = str(uuid.uuid4())
        logger.info(
            "🖼️ [DRAWINGS-TOOL] Rysunek '%s' utworzony w %s z %d elementami.",
            title,
            folder_path,
            len(elements),
        )
        return {
            "status": "TOOL_SUCCESS",
            "url": f"https://docs.google.com/drawings/{drawing_id}",
            "drawing_id": drawing_id,
        }
