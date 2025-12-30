# Plik: logos_orchestrator/mcp_server.py
# Cel: Implementacja serwera MCP dla integracji z gemini-cli (KROK 2.2)

from fastapi import APIRouter, Request, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
import logging
import os

logger = logging.getLogger("logos_orchestrator.mcp")

API_KEY_NAME = "X-MCP-API-Key"
mcp_api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# Zalecane: trzymać sekret w zmiennej środowiskowej lub Secret Manager
EXPECTED_API_KEY = os.environ.get("MCP_API_KEY", "TWOJ_SEKRETNY_KLUCZ_MCP_12345")

async def get_api_key(api_key: str = Security(mcp_api_key_header)):
    if api_key == EXPECTED_API_KEY:
        return api_key
    logger.warning("Nieudana próba dostępu do MCP (błędny klucz)")
    raise HTTPException(status_code=403, detail="Błędny lub brakujący klucz API")


router = APIRouter(prefix="/mcp", tags=["MCP-Server"], dependencies=[Depends(get_api_key)])


@router.post("/{command_name}")
async def handle_mcp_command(command_name: str, request: Request):
    logger.info(f"Otrzymano polecenie MCP: {command_name}")
    try:
        body = await request.json()
    except Exception:
        body = {}

    args = body.get("args", [])
    kwargs = body.get("kwargs", {})

    # Proste mocki operacji — zastąpić właściwą integracją
    if command_name == "check_job_status":
        job_id = kwargs.get("job_id")
        if not job_id:
            logger.error("Polecenie check_job_status wywołane bez --job_id")
            return {"error": "Brak wymaganego argumentu --job_id"}

        # TODO: Zintegrować z Supabase lub innym systemem przechowywania statusów
        status = f"COMPLETED"
        logger.info(f"Zwrócono status dla {job_id}: {status}")
        return {"prompt_text": f"Status zadania {job_id} to: {status}"}

    elif command_name == "run_paz_audit":
        pr_number = kwargs.get("pr_number")
        if not pr_number:
            logger.error("Polecenie run_paz_audit wywołane bez --pr_number")
            return {"error": "Brak wymaganego argumentu --pr_number"}

        # TODO: Zintegrować z GitHub API, workflowami itd.
        result = f"Mock: Ręczny audyt PAZ dla PR #{pr_number} został uruchomiony."
        logger.info(f"Uruchomiono audyt dla PR #{pr_number}")
        return {"prompt_text": result}

    else:
        logger.warning(f"Otrzymano nieznane polecenie MCP: {command_name}")
        return {"error": f"Nieznane polecenie MCP: {command_name}"}
