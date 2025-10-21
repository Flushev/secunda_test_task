from __future__ import annotations

from typing import List, TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model.base import Base

if TYPE_CHECKING:
    from app.model.activity import Activity
    from app.model.building import Building


class Organization(Base):
    __tablename__ = "organization"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phones: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    building_id: Mapped[int] = mapped_column(Integer, ForeignKey("building.id", ondelete="RESTRICT"), nullable=False)

    building: Mapped[Building] = relationship("Building", back_populates="organizations", init=False)

    activities: Mapped[list[Activity]] = relationship(
        "Activity", secondary="organization_activity", back_populates="organizations", viewonly=True, init=False
    )
