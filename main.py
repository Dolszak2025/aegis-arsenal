import os
import asyncio
from contextlib import asynccontextmanager
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.types import FlowControl
from faststream import FastStream, Logger
from faststream.redis import RedisBroker  # Lub inny broker wewnętrzny

# Używamy brokera (np. Redis lub Nats) do komunikacji wewnętrznej
# i zachowania logiki FastStream
broker = RedisBroker()
app = FastStream(broker)

# Inicjalizacja klienta Google Pub/Sub
subscriber_client = pubsub_v1.SubscriberClient()

# Odczytanie zmiennych środowiskowych
project_id = os.environ.get("PROJECT_ID")
subscription_id = os.environ.get("SUB_ID")

if not project_id or not subscription_id:
    raise ValueError("Brak zmiennych środowiskowych PROJECT_ID lub SUB_ID")

# Ścieżka subskrypcji zdefiniowana w Terraform (Tor 2)
subscription_path = f"projects/{project_id}/subscriptions/{subscription_id}"

async def pubsub_callback(
    message: pubsub_v1.subscriber.message.Message,
) -> None:
    """Callback dla klienta Google. Działa jak adapter."""
    logger = app.context.logger
    logger.info(f"Otrzymano wiadomość z Google Pub/Sub: {message.message_id}")

    try:
        # Przekazanie do wewnętrznego brokera FastStream
        # To pozwala nam używać dekoratorów, Pydantic, itp.
        await broker.publish(
            message.data,
            "internal_processing",
            headers={"google_message_id": message.message_id}
        )
        # Potwierdzenie wiadomości Google Pub/Sub PO pomyślnym opublikowaniu wewnętrznym
        message.ack()
    except Exception as e:
        logger.error(f"Błąd przetwarzania wewnętrznego: {e}")
        # Nie potwierdzaj (nack), aby Google spróbował ponownie (lub wysłał do DLQ)
        message.nack()

@broker.subscriber("internal_processing")
async def handle_message_faststream(body: bytes, logger: Logger):
    """
    Tutaj znajduje się właściwa logika biznesowa (Krok 1.4 / Faza 3).
    FastStream automatycznie parsuje 'body' jeśli podano typ Pydantic.
    """
    logger.info(f"Przetwarzanie wewnętrzne przez FastStream: {body.decode()}")
    #... wywołanie logiki LangGraph...

@app.on_startup
async def start_pubsub_listener():
    """Uruchomienie subskrybenta Google Pull w tle."""
    logger = app.context.logger
    logger.info("Uruchamianie subskrybenta Google Pub/Sub Pull...")

    # Krok 1.3: Użycie Flow Control. Jest to KRYTYCZNE dla stabilności
    # w Cloud Run, aby zapobiec przeciążeniu pojedynczej instancji.
    flow_control = FlowControl(
        max_messages=10,  # Ogranicz liczbę wiadomości przetwarzanych jednocześnie
        max_bytes=10 * 1024 * 1024  # 10 MB
    )

    streaming_pull_future = subscriber_client.subscribe(
        subscription_path,
        callback=pubsub_callback,
        flow_control=flow_control
    )

    logger.info(f"Rozpoczęto nasłuchiwanie na {subscription_path}")
    app.state.pubsub_future = streaming_pull_future

@app.on_shutdown
async def stop_pubsub_listener():
    """Zatrzymanie subskrybenta podczas zamykania."""
    if hasattr(app.state, "pubsub_future"):
        app.state.pubsub_future.cancel()
        await app.state.pubsub_future
