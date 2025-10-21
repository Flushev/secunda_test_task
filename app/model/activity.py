from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.model.base import Base

if TYPE_CHECKING:
    from app.model.organization import Organization


class Activity(Base):
    __tablename__ = "activity"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("activity.id", ondelete="CASCADE"), nullable=True, default=None
    )

    parent: Mapped[Activity | None] = relationship(
        "Activity", remote_side=[id], back_populates="childrens", lazy="selectin", init=False
    )
    childrens: Mapped[list[Activity]] = relationship("Activity", back_populates="parent", lazy="selectin", init=False)

    organizations: Mapped[list["Organization"]] = relationship(
        "Organization",
        secondary="organization_activity",
        back_populates="activities",
        viewonly=True,
        lazy="selectin",
        init=False,
    )

    @hybrid_property
    def depth(self) -> int:
        depth_value = 1
        node = self
        seen_ids: set[int] = set()
        while getattr(node, "parent", None) is not None:
            node_id = getattr(node, "id", None)
            if node_id is not None:
                if node_id in seen_ids:
                    break
                seen_ids.add(node_id)
            depth_value += 1
            node = node.parent  # type: ignore[assignment]
        return depth_value
