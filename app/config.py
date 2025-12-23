from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_user: str = "postgres"
    postgres_password: SecretStr = SecretStr("password")
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "postgres_db"
    sql_debug: bool = False
    media_folder: str = "media"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password.get_secret_value()}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()  # type: ignore
