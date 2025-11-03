import os
import asyncio
import google.cloud.logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.faststream import FastStreamInstrumentor

from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.types import FlowControl
from faststream import FastStream, Logger
from faststream.redis import RedisBroker
from faststream.opentelemetry import TelemetryMiddleware

from database import init_db_pool, get_db_pool, CustomAsyncPostgresSaver
# Placeholder for actual LangGraph types
# from langgraph.checkpoint.base import Checkpoint

# Krok 1.6: Korelacja Logów - Konfiguracja Google Cloud Logging
# Ta biblioteka automatycznie wykrywa kontekst OTel i dodaje pole `trace` do logów.
logging_client = google.cloud.logging.Client()
logging_client.setup_logging()

# Krok 1.6: Eleganckie Wykonanie - Automatyczna Propagacja OTel
# Konfiguracja OpenTelemetry SDK
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(None)) # W realnym scenariuszu tu byłby eksporter
trace.set_tracer_provider(provider)
FastStreamInstrumentor.instrument()

# Konfiguracja brokera wewnętrznego
broker = RedisBroker()

# Aplikacja FastStream z włączonym TelemetryMiddleware
app = FastStream(
    broker,
    middleware=[TelemetryMiddleware()],
)

# Inicjalizacja klienta Google Pub/Sub
subscriber_client = pubsub_v1.SubscriberClient()

# Odczytanie zmiennych środowiskowych
project_id = os.environ.get("GCP_PROJECT")
subscription_id = os.environ.get("SUB_ID")
supabase_conn_string = os.environ.get("SUPABASE_CONN_STRING")

if not all([project_id, subscription_id, supabase_conn_string]):
    raise ValueError("Brak kluczowych zmiennych środowiskowych: GCP_PROJECT, SUB_ID, SUPABASE_CONN_STRING")

subscription_path = f"projects/{project_id}/subscriptions/{subscription_id}"

async def pubsub_callback(message: pubsub_v1.subscriber.message.Message) -> None:
    """Adapter Google Pub/Sub -> FastStream."""
    logger = app.context.logger
    logger.info(f"Otrzymano wiadomość z Google Pub/Sub: {message.message_id}")
    try:
        await broker.publish(
            message.data,
            "internal_processing",
            headers={"google_message_id": message.message_id},
        )
        message.ack()
    except Exception as e:
        logger.error(f"Błąd przetwarzania wewnętrznego: {e}", exc_info=True)
        message.nack()

@broker.subscriber("internal_processing")
async def handle_message_faststream(body: bytes, logger: Logger):
    """
    Właściwa logika biznesowa zintegrowana z LangGraph i pulą połączeń.
    """
    logger.info(f"Przetwarzanie wewnętrzne przez FastStream: {body.decode()}")

    # Krok 1.5: Użycie wydajnego checkpointera
    # 1. Pobierz pulę połączeń zainicjowaną przy starcie
    pool = get_db_pool()
    # 2. Utwórz checkpointer, używając niestandardowej klasy i puli
    checkpointer = CustomAsyncPostgresSaver.from_pool(pool)

    # Przykład użycia (placeholder dla rzeczywistego wywołania LangGraph)
    logger.info("Pomyślnie utworzono checkpointer z puli połączeń.")
    # config = {"configurable": {"thread_id": "some_thread_id"}}
    # checkpoint = await checkpointer.aget(config)
    # logger.info(f"Pobrano checkpoint: {checkpoint}")

    # ... tutaj nastąpiłoby wywołanie logiki LangGraph ...
    # await langgraph_app.ainvoke(..., config={"checkpoint": checkpointer})

@app.on_startup
async def on_startup():
    """Uruchomienie nasłuchiwacza Pub/Sub i inicjalizacja puli DB."""
    logger = app.context.logger
    logger.info("Uruchamianie aplikacji...")

    # Inicjalizacja puli połączeń z bazą danych
    logger.info("Inicjalizowanie puli połączeń z bazą danych...")
    await init_db_pool(supabase_conn_string)

    # Konfiguracja Flow Control dla stabilności
    flow_control = FlowControl(max_messages=10)

    # Uruchomienie subskrybenta Google w tle
    streaming_pull_future = subscriber_client.subscribe(
        subscription_path, callback=pubsub_callback, flow_control=flow_control
    )

    logger.info(f"Rozpoczęto nasłuchiwanie na {subscription_path}")
    app.state.pubsub_future = streaming_pull_future

@app.on_shutdown
async def on_shutdown():
    """Zatrzymanie subskrybenta podczas zamykania."""
    logger = app.context.logger
    logger.info("Zamykanie aplikacji...")
    if hasattr(app.state, "pubsub_future"):
        app.state.pubsub_future.cancel()
        await asyncio.wait([app.state.pubsub_future], timeout=10)
        logger.info("Zatrzymano nasłuchiwacz Pub/Sub.")
