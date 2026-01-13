# Plik: logos_orchestrator/main.py
import logging
from fastapi import FastAPI
import uvicorn

# Konfiguracja logowania na samym początku
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("logos_orchestrator")

# ==========================================
# 1. IMPORTY MODUŁÓW (SOFT LOADING)
# ==========================================

# Telemetria (opcjonalna)
try:
    from .telemetry import setup_telemetry
except ImportError:
    logger.warning("⚠️ Moduł 'telemetry.py' nie został znaleziony. Uruchamianie w trybie bez telemetrii.")
    def setup_telemetry(app):
        pass # No-op

# MCP Server (Kluczowy moduł)
mcp_router = None
try:
    from .mcp_server import router as mcp_router
except ImportError as e:
    logger.error(f"❌ Błąd importu 'mcp_server': {}. Funkcje MCP będą niedostępne.")

# ==========================================
# 2. INICJALIZACJA APLIKACJI
# ==========================================

app = FastAPI(title="Logos Orchestrator", version="1.0.0")

# Aktywacja modułów
try:
    # 1. Uruchomienie telemetrii (np. OpenTelemetry / Prometheus)
    setup_telemetry(app)
    
    # 2. Rejestracja routera MCP
    if mcp_router:
        app.include_router(mcp_router)
        logger.info("✅ Podsystem MCP (Model Context Protocol) podłączony.")
    else:
        logger.warning("⚠️ Podsystem MCP nie został załadowany (brak modułu).")

    logger.info("🚀 System 'Zmysłów' i 'Połączenie' zainicjalizowane.")

except Exception as e:
    # Critical - jeśli tu coś padnie, aplikacja jest w stanie niestabilnym
    logger.critical(f"🔥 KRYTYCZNY BŁĄD podczas startu orkiestratora: {}", exc_info=True)


@app.get("/")
def read_root():
    status = {
        "system": "Logos Orchestrator",
        "status": "active",
        "modules": {
            "telemetry": "loaded", # Uproszczenie
            "mcp": "active" if mcp_router else "inactive"
        }
    }
    return status

# ==========================================
# 3. ENTRY POINT
# ==========================================
if __name__ == "__main__":
    # UWAGA: Używamy importu stringowego "logos_orchestrator.main:app"
    # To wymaga uruchomienia jako moduł (python -m ...)
    uvicorn.run(
        "logos_orchestrator.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=False, # Zmień na True podczas developmentu
        log_level="info"
    )