from __future__ import annotations

from typing import Iterable

from sqlalchemy.orm import Session

from app.crud.activity import activity_crud
from app.crud.building import building_crud
from app.crud.organization import organization_crud


def create_building(db: Session, address: str, lat: float, lon: float):
    return building_crud.create(db, {"address": address, "latitude": lat, "longitude": lon})


def create_activity(db: Session, name: str, parent_id: int | None = None):
    return activity_crud.create(db, {"name": name, "parent_id": parent_id})


def create_org(db: Session, name: str, building_id: int, phones: Iterable[str] = ()):
    return organization_crud.create(db, {"name": name, "building_id": building_id, "phones": list(phones)})


def set_org_activities(db: Session, org_id: int, activity_ids: Iterable[int]) -> None:
    organization_crud.set_activities(db, org_id, activity_ids)
