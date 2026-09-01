"""Application configuration for CineForecast backend service."""

from pathlib import Path
from typing import Any, List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                return json.loads(v)
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

    # Database & Cache
    DATABASE_URL: str = "sqlite:///./cineforecast.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Paths
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
    MODEL_REGISTRY_DIR: str = str(PROJECT_ROOT / "ml" / "models" / "registry")
    SHAP_CACHE_DIR: str = str(PROJECT_ROOT / "ml" / "models" / "registry" / "shap_cache")
    PROCESSED_DATA_DIR: str = str(PROJECT_ROOT / "data" / "processed")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
