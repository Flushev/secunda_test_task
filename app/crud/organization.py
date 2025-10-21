from __future__ import annotations

from typing import Iterable

from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.model.organization import Organization
from app.model.organization_activity import OrganizationActivity


class CRUDOrganization(CRUDBase[Organization]):
    def __init__(self) -> None:
        super().__init__(Organization)

    def set_activities(self, db: Session, org_id: int, activity_ids: Iterable[int]) -> None:
        ids = set(int(x) for x in activity_ids)
        # remove missing
        db.execute(
            delete(OrganizationActivity).where(
                OrganizationActivity.organization_id == org_id,
                OrganizationActivity.activity_id.not_in(ids) if ids else True,
            )
        )
        # add new
        if ids:
            existing = set(
                db.scalars(
                    select(OrganizationActivity.activity_id).where(OrganizationActivity.organization_id == org_id)
                )
            )
            to_insert = [{"organization_id": org_id, "activity_id": aid} for aid in ids - existing]
            if to_insert:
                db.execute(insert(OrganizationActivity), to_insert)


organization_crud = CRUDOrganization()
