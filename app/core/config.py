from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_cors_origins: str = Field(default="http://localhost:3000", alias="APP_CORS_ORIGINS")

    db_host: str | None = Field(default=None, alias="DB_HOST")
    db_port: int = Field(default=1433, alias="DB_PORT")
    db_name: str | None = Field(default=None, alias="DB_NAME")
    db_user: str | None = Field(default=None, alias="DB_USER")
    db_password: str | None = Field(default=None, alias="DB_PASSWORD")
    db_driver: str = Field(default="ODBC Driver 18 for SQL Server", alias="DB_DRIVER")
    db_encrypt: str = Field(default="yes", alias="DB_ENCRYPT")
    db_trust_server_cert: str = Field(default="no", alias="DB_TRUST_SERVER_CERT")
    db_connect_timeout: int = Field(default=5, alias="DB_CONNECT_TIMEOUT")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.app_cors_origins.split(",") if origin.strip()]

    @property
    def is_db_configured(self) -> bool:
        required = [self.db_host, self.db_name, self.db_user, self.db_password]
        return all(value and value.strip() for value in required)


@lru_cache
def get_settings() -> Settings:
    return Settings()
