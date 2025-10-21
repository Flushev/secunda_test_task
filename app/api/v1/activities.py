from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.activity import activity_crud
from app.schemas.activity import ActivityCreate, ActivityOut, ActivityUpdate


router = APIRouter()


@router.post("", response_model=ActivityOut, summary="Создание активности")
def create_activity(payload: ActivityCreate, db: Session = Depends(get_db)):
    """
    Данный метод позволяет создать новую активность. Нужен для проверки ограничений вложенности активностей.
    """
    obj = activity_crud.create(db, payload.model_dump(exclude_unset=True))
    return ActivityOut.model_validate(obj.__dict__)


@router.put("/{activity_id}", response_model=ActivityOut, summary="Обновление активности")
def update_activity(
    payload: ActivityUpdate,
    activity_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    """
    Данный метод позволяет обновить активность. Нужен для проверки ограничений вложенности активностей.
    """
    obj = activity_crud.require(db, activity_id)
    obj = activity_crud.update(db, obj, payload.model_dump(exclude_unset=True))
    return ActivityOut.model_validate(obj.__dict__)


@router.get("", response_model=list[ActivityOut], summary="Получение всех активностей")
def get_activities(
    limit: int = Query(50, ge=0, le=1000, description="Количество активностей на странице"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    db: Session = Depends(get_db),
):
    """
    Данный метод позволяет получить все активности.
    """
    objs = activity_crud.list(db, offset=offset, limit=limit)
    return [ActivityOut.model_validate(o.__dict__) for o in objs]
