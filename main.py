from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request, status  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
import uvicorn  # noqa: E402

from app.api.v1 import api_v1_router  # noqa: E402
from app.config.settings import settings  # noqa: E402
from app.crud.base import ValidationError  # noqa: E402


app = FastAPI(title="Secunda API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api/v1")


# Global exception handlers
@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal Server Error"})


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.app_host, port=settings.app_port, use_colors=True)
