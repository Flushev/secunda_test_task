from __future__ import annotations

from typing import List

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    api_key: str = Field(..., env="API_KEY")
    cors_origins: List[str] = Field(default_factory=lambda: ["*"], env="CORS_ORIGINS")
    app_host: str = Field("0.0.0.0", env="APP_HOST")
    app_port: int = Field(8000, env="APP_PORT")


def _parse_origins(value: List[str] | str) -> List[str]:
    if isinstance(value, list):
        return value
    if not value:
        return ["*"]
    return [item.strip() for item in value.split(",") if item.strip()]


settings = Settings()
settings.cors_origins = _parse_origins(settings.cors_origins)
