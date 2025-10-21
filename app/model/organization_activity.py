from __future__ import annotations

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.model.base import Base


class OrganizationActivity(Base):
    __tablename__ = "organization_activity"

    organization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organization.id", ondelete="CASCADE"), nullable=False, primary_key=True
    )
    activity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("activity.id", ondelete="CASCADE"), nullable=False, primary_key=True
    )
