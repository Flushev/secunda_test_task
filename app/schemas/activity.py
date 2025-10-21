from __future__ import annotations

from pydantic import BaseModel, Field


class ActivityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128, description="Название активности")
    parent_id: int | None = Field(default=None, description="ID родительской активности")


class ActivityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128, description="Название активности")
    parent_id: int | None = Field(default=None, description="ID родительской активности")


class ActivityOut(BaseModel):
    id: int = Field(description="ID активности")
    name: str = Field(description="Название активности")
    parent_id: int | None = Field(default=None, description="ID родительской активности")
