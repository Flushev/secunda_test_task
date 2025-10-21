from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255, description="Название организации")
    building_id: int = Field(description="ID здания")
    phones: List[str] = Field(default_factory=list, description="Телефоны организации")
    activity_ids: List[int] = Field(default_factory=list, description="ID активностей")


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255, description="Название организации")
    building_id: int | None = Field(default=None, description="ID здания")
    phones: List[str] | None = Field(default=None, description="Телефоны организации")
    activity_ids: List[int] | None = Field(default=None, description="ID активностей")


class OrganizationOut(BaseModel):
    id: int = Field(description="ID организации")
    name: str = Field(description="Название организации")
    building_id: int = Field(description="ID здания")
    phones: List[str] = Field(description="Телефоны организации")
