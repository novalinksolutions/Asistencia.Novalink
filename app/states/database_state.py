import reflex as rx
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError, OperationalError
import logging
from urllib.parse import urlparse, urlunparse, quote_plus

_engines_cache = {}
CLOUD_DB_HOST = "86.48.22.167"
CLOUD_DB_PORT = "5432"
CLOUD_DB_USER = "novalink"
CLOUD_DB_PASS = "Nov@link04$"
CLOUD_BASE_URL = f"postgresql://{CLOUD_DB_USER}:{quote_plus(CLOUD_DB_PASS)}@{CLOUD_DB_HOST}:{CLOUD_DB_PORT}/serviciosdev"


class DatabaseState(rx.State):
    """Base database state class for handling database connections and queries."""

    @rx.var
    def has_db_connection(self) -> bool:
        """Check if database connection is available."""
        return True

    def _get_base_url(self) -> str:
        """Get the base database URL, prioritizing local environment variables."""
        local_url = os.getenv("REFLEX_DB_URL")
        if local_url:
            return local_url
        return CLOUD_BASE_URL

    def _construct_db_url(self, base_url: str, target_db_name: str) -> str:
        """Construct a database URL for a specific database based on a base URL."""
        try:
            parsed = urlparse(base_url)
            new_path = f"/{target_db_name}"
            new_url = parsed._replace(path=new_path)
            return urlunparse(new_url)
        except Exception as e:
            logging.exception(f"Error constructing DB URL for {target_db_name}: {e}")
            if "/" in base_url.split("://")[1]:
                base_parts = base_url.rsplit("/", 1)
                return f"{base_parts[0]}/{target_db_name}"
            return f"{base_url}/{target_db_name}"

    def _get_db_engine(self, db_name: str):
        """Get or create a database engine for the specified database name."""
        global _engines_cache
        if not db_name:
            db_name = "novalink"
        if db_name in _engines_cache:
            return _engines_cache[db_name]
        base_url = self._get_base_url()
        is_local = "localhost" in base_url or "127.0.0.1" in base_url
        if is_local:
            logging.info(
                f"Ἶ Conectando a base de datos LOCAL ({db_name}): {urlparse(base_url).hostname}"
            )
        else:
            logging.info(
                f"☁️ Conectando a base de datos EN LA NUBE ({db_name}): {urlparse(base_url).hostname}"
            )
        url = None
        if db_name == "novalink":
            env_novalink = os.getenv("NOVALINK_DB_URL")
            if env_novalink:
                url = env_novalink
                logging.info("⚡ Using explicit NOVALINK_DB_URL from environment")
            else:
                url = self._construct_db_url(base_url, "novalink")
        elif db_name == "serviciosdev":
            url = self._construct_db_url(base_url, "serviciosdev")
        else:
            url = self._construct_db_url(base_url, db_name)
        if not url:
            logging.error(f"No connection URL constructed for database: {db_name}")
            return None
        try:
            logging.debug(
                f"Creating new database engine for: {db_name} -> {url.split('@')[-1]}"
            )
            engine = create_engine(
                url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                pool_recycle=1800,
                connect_args={
                    "connect_timeout": 10,
                    "keepalives": 1,
                    "keepalives_idle": 30,
                    "keepalives_interval": 10,
                    "keepalives_count": 5,
                },
            )
            _engines_cache[db_name] = engine
            logging.info(f"✅ Engine created for {db_name}")
            return engine
        except Exception as e:
            logging.exception(f"Error creating database engine for {db_name}: {e}")
            return None

    @rx.event
    def verify_connection(self, db_name: str) -> bool:
        """Verify that a connection to the specified database can be established."""
        try:
            engine = self._get_db_engine(db_name)
            if not engine:
                return False
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logging.exception(f"Connection verification failed for {db_name}: {e}")
            return False

    async def _execute_query(
        self, query: str, params: dict = None, target_db: str | None = None
    ) -> list[dict[str, object]]:
        """Execute a database query and return results using the active database or a specific target."""
        from app.states.base_state import BaseState

        current_db = "serviciosdev"
        try:
            if target_db:
                current_db = target_db
            else:
                base_state = await self.get_state(BaseState)
                current_db = base_state.current_database_name or "novalink"
            logging.debug(f"Executing query on {current_db}")
            engine = self._get_db_engine(current_db)
            if not engine:
                logging.error(f"Failed to get engine for database: {current_db}")
                return []
            with engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                if result.returns_rows:
                    columns = result.keys()
                    rows = result.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
                return []
        except ProgrammingError as e:
            if "relation" in str(e) and "does not exist" in str(e):
                logging.warning(f"Table not found in database {current_db}: {e}")
            else:
                logging.exception(f"Database programming error in {current_db}: {e}")
            return []
        except OperationalError as e:
            logging.exception(f"Database operational error in {current_db}: {e}")
            global _engines_cache
            if current_db in _engines_cache:
                logging.info(
                    f"Invalidating engine cache for {current_db} due to operational error"
                )
                del _engines_cache[current_db]
            return []
        except Exception as e:
            logging.exception(f"Error executing query in {current_db}: {e}")
            return []

    async def _execute_write(
        self, query: str, params: dict = None, target_db: str | None = None
    ):
        """Execute a write operation (INSERT, UPDATE, DELETE) with transaction commit."""
        from app.states.base_state import BaseState

        current_db = "serviciosdev"
        try:
            if target_db:
                current_db = target_db
            else:
                base_state = await self.get_state(BaseState)
                current_db = base_state.current_database_name or "novalink"
            engine = self._get_db_engine(current_db)
            if not engine:
                raise Exception(f"No connection to database {current_db}")
            with engine.begin() as conn:
                conn.execute(text(query), params or {})
        except OperationalError as e:
            logging.exception(f"Write operation connection error in {current_db}: {e}")
            global _engines_cache
            if current_db in _engines_cache:
                del _engines_cache[current_db]
            raise e
        except Exception as e:
            logging.exception(f"Error executing write in {current_db}: {e}")
            raise e

    @rx.event
    async def execute_query(
        self, query: str, params: dict = None, target_db: str | None = None
    ):
        """Wrapper event for executing queries from frontend."""
        await self._execute_query(query, params, target_db)