# Plik: logos_orchestrator/main.py
# Cel: Główny plik aplikacji, integrujący Telemetrię i MCP

from fastapi import FastAPI
import logging
import uvicorn

# Importujemy nasze moduły (telemetry.py powinien istnieć w tym pakiecie)
try:
    from .telemetry import setup_telemetry  # optional
except Exception:
    def setup_telemetry(app):
        # fallback: noop
        return

from .mcp_server import router as mcp_router

# Konfiguracja podstawowego loggingu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("logos_orchestrator")

app = FastAPI()

# --- AKTYWACJA MODUŁÓW ---
try:
    setup_telemetry(app)
    app.include_router(mcp_router)
    logger.info("System 'Zmysłów' (Telemetry) i 'Połączenie' (MCP) zostały pomyślnie załadowane.")
except Exception as e:
    logger.critical(f"KRYTYCZNY BŁĄD podczas inicjalizacji modułów: {e}", exc_info=True)


@app.get("/")
def read_root():
    return {"message": "logos-orchestrator jest aktywny. Telemetria i MCP są załadowane."}


if __name__ == "__main__":
    uvicorn.run("logos_orchestrator.main:app", host="0.0.0.0", port=8000, reload=False)
