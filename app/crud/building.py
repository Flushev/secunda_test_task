from __future__ import annotations


from app.crud.base import CRUDBase
from app.model.building import Building


class CRUDBuilding(CRUDBase[Building]):
    def __init__(self) -> None:
        super().__init__(Building)


building_crud = CRUDBuilding()
