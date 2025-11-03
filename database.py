import psycopg
import contextlib
from typing import AsyncIterator
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from langchain_postgres import AsyncPostgresSaver

# Krok 1.5: Eleganckie Wykonanie - Zgodność z Supabase i Wydajność
# Używamy puli połączeń, aby uniknąć tworzenia nowego połączenia przy każdym
# wywołaniu checkpointera LangGraph. Pula jest inicjowana przy starcie aplikacji.
db_pool: AsyncConnectionPool | None = None

def get_db_pool() -> AsyncConnectionPool:
    """Zwraca zainicjowaną pulę połączeń."""
    if db_pool is None:
        raise RuntimeError("Pula połączeń z bazą danych nie została zainicjowana.")
    return db_pool

async def init_db_pool(conninfo: str):
    """Inicjalizuje pulę połączeń psycopg."""
    global db_pool
    if db_pool is None:
        db_pool = AsyncConnectionPool(
            conninfo=conninfo,
            # Ustawienia puli, np. min/max liczba połączeń
            min_size=1,
            max_size=5,
            # Konfiguracja połączenia - kluczowe dla Supabase
            kwargs={
                "sslmode": "require", # Wymuszenie SSL dla Supabase
                "autocommit": True,   # Zalecane dla wydajności
                "row_factory": dict_row
            }
        )
        # Sprawdzenie połączenia
        try:
            async with db_pool.connection() as conn:
                await conn.execute("SELECT 1")
            print("Pomyślnie zainicjowano pulę połączeń z bazą danych.")
        except Exception as e:
            print(f"Błąd inicjalizacji puli połączeń: {e}")
            db_pool = None # Resetuj w razie błędu
            raise

class CustomAsyncPostgresSaver(AsyncPostgresSaver):
    """
    Niestandardowa implementacja, która używa puli połączeń zamiast
    tworzyć nowe połączenie za każdym razem. Jest to znacznie bardziej wydajne.
    """
    def __init__(self, *, pool: AsyncConnectionPool, **kwargs):
        # Inicjalizujemy klasę bazową, ale pomijamy przekazywanie `conn`
        # ponieważ będziemy zarządzać połączeniami za pomocą puli.
        super().__init__(conn=None, **kwargs)
        self.pool = pool

    @classmethod
    def from_conn_string(cls, conn_string: str) -> "CustomAsyncPostgresSaver":
        raise NotImplementedError(
            "Użyj `from_pool` zamiast `from_conn_string` "
            "w tej niestandardowej implementacji."
        )

    @classmethod
    def from_pool(cls, pool: AsyncConnectionPool) -> "CustomAsyncPostgresSaver":
        """Tworzy instancję, używając istniejącej puli połączeń."""
        return cls(pool=pool)

    @contextlib.asynccontextmanager
    async def _get_connection(self) -> AsyncIterator[psycopg.AsyncConnection]:
        """Pobiera połączenie z puli."""
        async with self.pool.connection() as conn:
            yield conn
