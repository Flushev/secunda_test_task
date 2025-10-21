from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.building import building_crud
from app.schemas.building import BuildingOut


router = APIRouter()


@router.get("", response_model=list[BuildingOut], summary="List buildings")
def list_buildings(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return building_crud.list(db, limit=limit, offset=offset)
