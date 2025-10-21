from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase, ValidationError
from app.model.activity import Activity


MAX_DEPTH = 3


def check_depth(db: Session, parent_id: int | None, current_id: int | None) -> None:
    if parent_id is None:
        return
    parent = db.get(Activity, parent_id)
    if parent.depth == MAX_DEPTH:
        raise ValidationError(
            f"CRUD error for Activity object {current_id or ''} in parent category {parent_id}: nesting depth must be <= {MAX_DEPTH}. Parent depth: {parent.depth}"
        )


class CRUDActivity(CRUDBase[Activity]):
    def __init__(self) -> None:
        super().__init__(Activity)

    def create(self, db: Session, data: dict[str, Any]) -> Activity:
        check_depth(db, data.get("parent_id"), data.get("id"))
        return super().create(db, data)

    def update(self, db: Session, obj: Activity, data: dict[str, Any]) -> Activity:
        parent_id = data.get("parent_id", obj.parent_id)
        check_depth(db, parent_id, obj.id)
        if obj.id is not None and parent_id == obj.id:
            raise ValidationError(f"CRUD error for Activity object {obj.id}: cannot be parent of itself")
        return super().update(db, obj, data)


activity_crud = CRUDActivity()
