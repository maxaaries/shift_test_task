from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str
    DEBUG: bool = False
    HOST_PORT: int = 8081

    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_HOST: str = "localhost"
    DB_PORT: int
    DATABASE_ECHO: bool
    DATABASE_URL: str | None = None

    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @property
    def database_echo(self) -> bool:
        return self.DATABASE_ECHO

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL.replace("+asyncpg", "+psycopg").replace(
                "+psycopg2", "+psycopg"
            )
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def sync_database_url(self) -> str:
        return self.async_database_url


settings = Settings()
