from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config.settings import settings


api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def require_api_key(key: str | None = Security(api_key_header)) -> None:
    if not key or key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
