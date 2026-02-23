# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    encryption_key: str 

    class Config:
        env_file = ".env"
        extra = "ignore" 
settings = Settings()
