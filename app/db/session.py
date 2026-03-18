from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.config import get_settings


def build_connection_url() -> str:
    settings = get_settings()

    if not settings.is_db_configured:
        raise ValueError("Missing required DB env vars: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD")

    params = (
        f"DRIVER={{{settings.db_driver}}};"
        f"SERVER={settings.db_host},{settings.db_port};"
        f"DATABASE={settings.db_name};"
        f"UID={settings.db_user};"
        f"PWD={settings.db_password};"
        f"Encrypt={settings.db_encrypt};"
        f"TrustServerCertificate={settings.db_trust_server_cert};"
        f"Connection Timeout={settings.db_connect_timeout};"
    )

    return f"mssql+pyodbc:///?odbc_connect={quote_plus(params)}"


def get_engine() -> Engine:
    return create_engine(build_connection_url(), pool_pre_ping=True, future=True)


def test_db_connection() -> tuple[bool, str]:
    try:
        engine = get_engine()
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, "Connected to SQL Server"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
