from __future__ import annotations


from sqlalchemy.orm import Session

from app.config.db import SqlAlchemyConfig


def get_db() -> Session:
    with SqlAlchemyConfig.session(autoflush=False, autocommit=False, expire_on_commit=False) as db:
        try:
            yield db
        except Exception:
            db.rollback()
            raise
        else:
            db.commit()
