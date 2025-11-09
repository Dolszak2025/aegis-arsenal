from typing import Any, Dict, List
from abc import ABC, abstractmethod
import uuid
import logging
import os

logger = logging.getLogger("logos_orchestrator.tools.google_drawings")


class BaseTool(ABC):
    """Prosta klasa bazowa dla narzędzi. Jeśli w projekcie istnieje inna
    definicja `BaseTool`, preferuj jej import zamiast tego pliku.
    """

    name: str = "base_tool"
    description: str = "Base tool"

    @abstractmethod
    def get_function_definition(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError


class GoogleDrawingsTool(BaseTool):
    """
    Symulowane narzędzie do tworzenia diagramów/rysunków (Google Drawings).

    Parametry:
    - title: tytuł rysunku
    - elements: lista elementów diagramu (symulacja: shape/text/line/arrow)
    - folder_path: miejsce zapisu w Drive (np. PSC_REPORTS)
    - style_template: opcjonalny szablon stylu

    Zwraca URL symulowanego rysunku oraz meta.
    """

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
                    "title": {"type": "string", "description": "Tytuł rysunku"},
                    "elements": {
                        "type": "array",
                        "description": "Lista elementów diagramu (np. {'type':'box','text':'..'})",
                    },
                    "folder_path": {"type": "string", "description": "Ścieżka folderu w Drive (np. 'PSC_REPORTS')"},
                    "style_template": {"type": "string", "description": "Opcjonalny opis stylu diagramu (np. 'technical-diagram')"},
                },
                "required": ["title", "elements", "folder_path"],
            },
        }

    def execute(
        self,
        title: str,
        elements: List[Dict[str, Any]],
        folder_path: str,
        style_template: str = "Standard Diagram",
    ) -> Dict[str, Any]:
        """
        Wersja symulacyjna: generuje losowe ID i zwraca URL do "docs.google.com/drawings".
        W produkcji tu by była integracja z Drive API / generowanie SVG lub Slides.
        """

        drawing_id = str(uuid.uuid4())

        # Logujemy kilka elementów, ale ograniczamy liczbę aby nie zalewać logów
        logger.info(
            "🖼️ [DRAWINGS-TOOL] Tworzę rysunek: '%s' w folderze '%s' wg szablonu '%s'. Elementów: %d",
            title,
            folder_path,
            style_template,
            len(elements),
        )

        # Debug: wypisz do 10 elementów
        for i, el in enumerate(elements[:10]):
            logger.debug("  - el[%d]: %s", i, el)

        # Symulacja: w produkcji tutaj wyślesz elementy do API i otrzymasz URL
        url = f"https://docs.google.com/drawings/{drawing_id}"

        return {
            "status": "TOOL_SUCCESS",
            "message": f"Rysunek '{title}' utworzony (symulacja).",
            "url": url,
            "drawing_id": drawing_id,
            "meta": {"title": title, "elements_count": len(elements), "style_template": style_template, "folder_path": folder_path},
        }


# Optional: umożliwiamy import klasy z tego modułu jako domyślnego narzędzia
__all__ = ["GoogleDrawingsTool", "BaseTool"]
