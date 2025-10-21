from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model.base import Base

if TYPE_CHECKING:
    from app.model.organization import Organization


class Building(Base):
    __tablename__ = "building"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    organizations: Mapped[list[Organization]] = relationship("Organization", back_populates="building", init=False)
