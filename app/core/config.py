from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    ENCRYPTION_KEY: str
    AI_BACKEND_URL: str = "http://127.0.0.1:8001"
    APP_TIMEZONE: str = "Asia/Colombo"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()