from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    AI_BACKEND_URL: str
    ENCRYPTION_KEY: str
    APP_TIMEZONE: str = "Asia/Colombo"
    FIREBASE_CREDENTIALS_PATH: str
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()