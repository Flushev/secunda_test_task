from __future__ import annotations

from typing import Iterable

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.activity import MAX_DEPTH
from app.model.activity import Activity
from app.model.building import Building
from app.model.organization import Organization
from app.schemas.organization import OrganizationOut


router = APIRouter()


def _collect_activity_subtree_ids(db: Session, roots: Iterable[int]) -> set[int]:
    all_ids: set[int] = set(int(r) for r in roots)
    frontier: set[int] = set(all_ids)
    for _ in range(MAX_DEPTH):
        if not frontier:
            break
        rows = db.execute(select(Activity.id).where(Activity.parent_id.in_(frontier))).scalars().all()
        new_ids = set(rows) - all_ids
        if not new_ids:
            break
        all_ids |= new_ids
        frontier = new_ids
    return all_ids


@router.get("/search", response_model=list[OrganizationOut], summary="Поиск организаций по названию активности")
def get_organization(
    activity_name: str = Query(description="Название активности"),
    limit: int = Query(50, ge=0, le=1000, description="Количество организаций на странице"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    db: Session = Depends(get_db),
):
    """
    Данный метод позволяет найти все организации, активность которых входит в дерево заданной активности.
    """
    stmt = select(Organization)
    roots: list[int] = []
    rows = db.execute(select(Activity.id).where(func.lower(Activity.name) == func.lower(activity_name))).scalars().all()
    roots.extend(rows)
    if roots:
        activity_ids = _collect_activity_subtree_ids(db, roots)

        if activity_ids:
            stmt = stmt.join(Organization.activities).where(Activity.id.in_(activity_ids))

    stmt = stmt.offset(offset).limit(limit)

    objs = list(db.scalars(stmt))
    return [OrganizationOut.model_validate(o.__dict__) for o in objs]


class OrganizationFilter(BaseModel):
    building_id: int | None = Field(default=None, description="ID здания")
    organization_id: int | None = Field(default=None, description="ID организации")
    organization_name: str | None = Field(default=None, min_length=1, description="Название организации")
    activity_name: str | None = Field(default=None, min_length=1, description="Название активности")


@router.post("/filter", response_model=list[OrganizationOut], summary="Фильтрация организаций")
def get_organization_by_filter(
    payload: OrganizationFilter,
    limit: int = Query(50, ge=0, le=1000, description="Количество организаций на странице"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    db: Session = Depends(get_db),
):
    """
    Данный метод позволяет найти все организации, которые соответствуют указанным фильтрам.
    """
    stmt = select(Organization)

    if payload.organization_id:
        stmt = stmt.where(Organization.id == payload.organization_id)

    if payload.organization_name:
        like = f"%{payload.organization_name}%"
        stmt = stmt.where(func.lower(Organization.name).like(func.lower(like)))

    if payload.building_id:
        stmt = stmt.where(Organization.building_id == payload.building_id)

    if payload.activity_name:
        like = f"%{payload.activity_name}%"
        stmt = stmt.join(Organization.activities).where(func.lower(Activity.name).like(func.lower(like)))

    stmt = stmt.offset(offset).limit(limit)

    objs = list(db.scalars(stmt))
    return [OrganizationOut.model_validate(o.__dict__) for o in objs]


@router.get("/nearby/radius", response_model=list[OrganizationOut], summary="Организации в заданном радиусе")
def organizations_nearby_radius(
    center_lat: float = Query(..., description="Широта центра"),
    center_lon: float = Query(..., description="Долгота центра"),
    radius: float = Query(..., ge=0, description="Радиус"),
    limit: int = Query(50, ge=1, le=1000, description="Количество организаций на странице"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    db: Session = Depends(get_db),
):
    """
    Данный метод позволяет найти все организации, которые находятся в заданном радиусе.
    """
    stmt = select(Organization).join(Organization.building)
    center = func.Point(center_lon, center_lat)
    location = func.Point(Building.longitude, Building.latitude)
    distance = func.ST_Distance_Sphere(center, location)
    stmt = stmt.where(distance <= radius)
    stmt = stmt.offset(offset).limit(limit)
    objs = list(db.scalars(stmt))
    return [OrganizationOut.model_validate(o.__dict__) for o in objs]


@router.get("/nearby/square", response_model=list[OrganizationOut], summary="Организации в заданном прямоугольнике")
def organizations_nearby_square(
    lat_min: float = Query(..., description="Широта от"),
    lat_max: float = Query(..., description="Широта до"),
    lon_min: float = Query(..., description="Долгота от"),
    lon_max: float = Query(..., description="Долгота до"),
    limit: int = Query(50, ge=1, le=1000, description="Количество организаций на странице"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    db: Session = Depends(get_db),
):
    """
    Данный метод позволяет найти все организации, которые находятся в заданном прямоугольнике.
    """
    stmt = select(Organization).join(Organization.building)
    stmt = stmt.where(
        Building.latitude.between(lat_min, lat_max),
        Building.longitude.between(lon_min, lon_max),
    )
    stmt = stmt.offset(offset).limit(limit)
    objs = list(db.scalars(stmt))
    return [OrganizationOut.model_validate(o.__dict__) for o in objs]
