from fastapi import APIRouter, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import os
import secrets

logger = logging.getLogger("logos_orchestrator.mcp")

# ==========================================
# 1. KONFIGURACJA BEZPIECZEŃSTWA
# ==========================================
API_KEY_NAME = "X-MCP-API-Key"
mcp_api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# Pobieramy klucz ze zmiennych, z bezpiecznym fallbackiem (nie używać fallbacku na prod!)
EXPECTED_API_KEY = os.environ.get("MCP_API_KEY", "TWOJ_SEKRETNY_KLUCZ_MCP_12345")

async def get_api_key(api_key: str = Security(mcp_api_key_header)):
    # secrets.compare_digest zapobiega atakom czasowym (timing attacks)
    if secrets.compare_digest(api_key, EXPECTED_API_KEY):
        return api_key
    
    logger.warning(f"⛔ Nieautoryzowana próba dostępu do MCP. Klucz: {api_key[:4]}***")
    raise HTTPException(status_code=403, detail="Błędny lub brakujący klucz API")

# ==========================================
# 2. MODELE DANYCH (PYDANTIC)
# ==========================================
class MCPRequest(BaseModel):
    """Model oczekiwanego body JSON od klienta (np. gemini-cli)"""
    args: List[Any] = Field(default_factory=list)
    kwargs: Dict[str, Any] = Field(default_factory=dict)

class MCPResponse(BaseModel):
    """Ujednolicony format odpowiedzi"""
    prompt_text: Optional[str] = None
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

# ==========================================
# 3. LOGIKA BIZNESOWA (HANDLERS)
# ==========================================

async def cmd_check_job_status(kwargs: Dict[str, Any]) -> MCPResponse:
    job_id = kwargs.get("job_id")
    if not job_id:
        return MCPResponse(error="Brak wymaganego argumentu --job_id")

    # MOCK: Integracja z bazą danych / Cloud Build
    status = "COMPLETED" # Tu wstawisz realną logikę
    
    logger.info(f"Sprawdzono status zadania {job_id}: {status}")
    return MCPResponse(
        prompt_text=f"Status zadania {job_id} to: {status}",
        data={"job_id": job_id, "status": status}
    )

async def cmd_run_paz_audit(kwargs: Dict[str, Any]) -> MCPResponse:
    pr_number = kwargs.get("pr_number")
    if not pr_number:
        return MCPResponse(error="Brak wymaganego argumentu --pr_number")

    # MOCK: Trigger GitHub Actions / Jenkins
    logger.info(f"Uruchomiono audyt PAZ dla PR #{pr_number}")
    return MCPResponse(
        prompt_text=f"Ręczny audyt PAZ dla PR #{pr_number} został zlecony.",
        data={"pr": pr_number, "action": "audit_triggered"}
    )

async def cmd_get_version(kwargs: Dict[str, Any]) -> MCPResponse:
    return MCPResponse(prompt_text="Logos Orchestrator v1.0.0 (MCP Active)")

# ==========================================
# 4. REJESTR KOMEND
# ==========================================
# Mapa: nazwa_komendy -> funkcja_obsługująca
COMMAND_REGISTRY = {
    "check_job_status": cmd_check_job_status,
    "run_paz_audit": cmd_run_paz_audit,
    "version": cmd_get_version
}

# ==========================================
# 5. ROUTING
# ==========================================
router = APIRouter(prefix="/mcp", tags=["MCP-Server"], dependencies=[Depends(get_api_key)])

@router.post("/{command_name}", response_model=MCPResponse)
async def handle_mcp_command(command_name: str, payload: MCPRequest):
    """
    Uniwersalny endpoint przyjmujący polecenia MCP.
    Dispatchuje do odpowiedniej funkcji z COMMAND_REGISTRY.
    """
    logger.info(f"📥 Otrzymano polecenie MCP: {command_name} | Args: {payload.kwargs}")

    handler = COMMAND_REGISTRY.get(command_name)
    
    if not handler:
        logger.warning(f"⚠️ Nieznane polecenie: {command_name}")
        return MCPResponse(error=f"Nieznane polecenie MCP: {command_name}")

    try:
        # Wywołanie odpowiedniej funkcji
        result = await handler(payload.kwargs)
        return result
    except Exception as e:
        logger.error(f"🔥 Błąd podczas wykonywania {command_name}: {}", exc_info=True)
        return MCPResponse(error=f"Wystąpił błąd wewnętrzny serwera: {str(e)}")