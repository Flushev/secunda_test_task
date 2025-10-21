from __future__ import annotations

from typing import Any, Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.model.base import Base


ModelType = TypeVar("ModelType", bound=Base)


class ValidationError(Exception):
    pass


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> ModelType | None:
        return db.get(self.model, id)

    def require(self, db: Session, id: int) -> ModelType:
        obj = self.get(db, id)
        if obj is None:
            raise ValidationError(f"{self.model.__name__}({id}) not found")
        return obj

    def list(self, db: Session, *, offset: int = 0, limit: int = 50) -> list[ModelType]:
        stmt = select(self.model).offset(offset).limit(limit)
        return list(db.scalars(stmt))

    def create(self, db: Session, data: dict[str, Any]) -> ModelType:
        obj = self.model(**data)
        db.add(obj)
        db.flush()
        db.refresh(obj)
        return obj

    def update(self, db: Session, obj: ModelType, data: dict[str, Any]) -> ModelType:
        for key, value in data.items():
            if value is not None:
                setattr(obj, key, value)
        db.flush()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, obj: ModelType) -> None:
        db.delete(obj)
        db.flush()
