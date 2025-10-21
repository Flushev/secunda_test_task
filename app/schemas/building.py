from __future__ import annotations

from pydantic import BaseModel, Field


class BuildingCreate(BaseModel):
    address: str = Field(min_length=1, max_length=255, description="Адрес здания")
    latitude: float = Field(description="Широта")
    longitude: float = Field(description="Долгота")


class BuildingUpdate(BaseModel):
    address: str | None = Field(default=None, min_length=1, max_length=255)
    latitude: float | None = Field(default=None, description="Широта")
    longitude: float | None = Field(default=None, description="Долгота")


class BuildingOut(BaseModel):
    id: int = Field(description="ID здания")
    address: str = Field(description="Адрес здания")
    latitude: float = Field(description="Широта")
    longitude: float = Field(description="Долгота")
