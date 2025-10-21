#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from typing import Dict, List, Tuple

from dotenv import load_dotenv

from app.config.db import SqlAlchemyConfig

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.activity import activity_crud
from app.crud.building import building_crud
from app.crud.organization import organization_crud
from app.model.activity import Activity
from app.model.building import Building
from app.model.organization import Organization



load_dotenv()


def seed_buildings(db: Session) -> Dict[str, int]:
    buildings: List[Tuple[str, float, float]] = [
        ("г. Москва, ул. Ленина 1", 55.7558, 37.6176),  # center
        ("г. Москва, ул. Тверская 10", 55.7570, 37.6150),  # ~200m from center
        ("г. Москва, пр-т Мира 50", 55.7890, 37.6320),
        ("г. Санкт-Петербург, Невский проспект 100", 59.9340, 30.3350),
        ("г. Новосибирск, Красный проспект 1", 55.0300, 82.9200),
        ("г. Екатеринбург, ул. Ленина 50", 56.8380, 60.6050),
    ]
    addr_to_id: Dict[str, int] = {}
    for address, lat, lon in buildings:
        existing_id = db.execute(select(Building.id).where(Building.address == address)).scalar_one_or_none()
        if existing_id:
            addr_to_id[address] = existing_id
            continue
        obj = building_crud.create(db, {"address": address, "latitude": lat, "longitude": lon})
        addr_to_id[address] = obj.id
    return addr_to_id


def _get_activity_by_name_parent(db: Session, name: str, parent_id: int | None) -> int | None:
    return db.execute(
        select(Activity.id).where(
            Activity.name == name,
            Activity.parent_id.is_(None) if parent_id is None else Activity.parent_id == parent_id,
        )
    ).scalar_one_or_none()


def seed_activities(db: Session) -> Dict[str, int]:
    tree = {
        "name": "Главная категория",
        "child": [
            {
                "name": "Еда",
                "child": [
                    {
                        "name": "Мясная продукция",
                        "child": [],
                    },
                    {
                        "name": "Молочная продукция",
                        "child": [],
                    },
                ],
            },
            {
                "name": "Автомобили",
                "child": [
                    {
                        "name": "Грузовые",
                        "child": [],
                    },
                    {
                        "name": "Легковые",
                        "child": [],
                    },
                ],
            },
            {
                "name": "Услуги",
                "child": [
                    {
                        "name": "Ремонт",
                        "child": [],
                    },
                    {
                        "name": "Доставка",
                        "child": [],
                    },
                ],
            },
            {
                "name": "Спорту",
                "child": [
                    {
                        "name": "Экипировка",
                        "child": [],
                    },
                    {
                        "name": "Фитнес",
                        "child": [],
                    },
                ],
            },
        ],
    }

    name_to_id: Dict[str, int] = {}

    def ensure_activity(name: str, parent_id: int | None) -> int:
        act_id = _get_activity_by_name_parent(db, name, parent_id)
        if act_id:
            return act_id
        data = {"name": name, "parent_id": parent_id}
        if parent_id is None:
            obj = Activity(name=name, parent_id=None)
            db.add(obj)
            db.flush()
            db.refresh(obj)
            return obj.id
        obj = activity_crud.create(db, data)
        return obj.id

    def walk_node(node: dict, parent_id: int | None) -> None:
        name = node.get("name")
        if not name:
            return
        act_id = ensure_activity(name, parent_id)
        name_to_id[name] = act_id
        children = node.get("child") or []
        for child in children:
            walk_node(child, act_id)

    walk_node(tree, None)

    return name_to_id


def seed_organizations(db: Session, addr_to_id: Dict[str, int], name_to_act_id: Dict[str, int]) -> None:
    data_rows = [
        {
            "name": "ЕдаМаркет",
            "address": "г. Москва, ул. Ленина 1",
            "phones": ["2-222-222", "8-923-666-13-13"],
            "activities": ["Еда"],
        },
        {
            "name": "Мясной рай",
            "address": "г. Москва, ул. Ленина 1",
            "phones": ["3-333-333"],
            "activities": ["Мясная продукция"],
        },
        {
            "name": "Молочка+",
            "address": "г. Москва, ул. Тверская 10",
            "phones": ["8-900-111-22-33"],
            "activities": ["Молочная продукция"],
        },
        {
            "name": "АвтоГруз",
            "address": "г. Москва, пр-т Мира 50",
            "phones": ["+7-495-000-00-01"],
            "activities": ["Грузовые"],
        },
        {
            "name": "Запчасти 24",
            "address": "г. Москва, пр-т Мира 50",
            "phones": ["+7-495-000-00-02"],
            "activities": ["Запчасти"],
        },
        {
            "name": "Аксессуары PRO",
            "address": "г. Москва, ул. Тверская 10",
            "phones": ["+7-495-000-00-03"],
            "activities": ["Аксессуары"],
        },
        {
            "name": "Фитнес-спорт",
            "address": "г. Санкт-Петербург, Невский проспект 100",
            "phones": ["+7-812-777-77-77"],
            "activities": ["Фитнес"],
        },
        {
            "name": "Сервис Ремонт",
            "address": "г. Новосибирск, Красный проспект 1",
            "phones": ["+7-383-222-22-22"],
            "activities": ["Ремонт"],
        },
        {
            "name": "ДоставкаЕды",
            "address": "г. Москва, ул. Ленина 1",
            "phones": ["+7-999-123-45-67"],
            "activities": ["Еда", "Доставка"],
        },
        {
            "name": "Еда маркет",
            "address": "г. Екатеринбург, ул. Ленина 50",
            "phones": ["+7-343-100-00-01"],
            "activities": ["Еда"],
        },
        {
            "name": "NullActivities",
            "address": "г. Новосибирск, Красный проспект 1",
            "phones": [],
            "activities": [],
        },
        {
            "name": "БлизкоКЦентру",
            "address": "г. Москва, ул. Тверская 10",
            "phones": ["+7-495-000-00-04"],
            "activities": ["Молочная продукция"],
        },
    ]

    for row in data_rows:
        name = row["name"]
        org_id = db.execute(select(Organization.id).where(Organization.name == name)).scalar_one_or_none()
        payload = {
            "name": name,
            "building_id": addr_to_id[row["address"]],
            "phones": row["phones"],
        }
        if org_id:
            org = db.get(Organization, org_id)
            assert org is not None
            org.building_id = payload["building_id"]
            org.phones = payload["phones"]
            db.flush()
        else:
            org = organization_crud.create(db, payload)

        # Set activities
        act_ids = [name_to_act_id[a] for a in row["activities"] if a in name_to_act_id]
        if act_ids:
            organization_crud.set_activities(db, org.id, act_ids)


def main() -> int:
    from app.model.base import Base

    Base.metadata.create_all(SqlAlchemyConfig.engine())
    with SqlAlchemyConfig.session() as db:
        addr_to_id = seed_buildings(db)
        name_to_act_id = seed_activities(db)
        seed_organizations(db, addr_to_id, name_to_act_id)

        db.commit()
        print("Seed complete")
        return 0


if __name__ == "__main__":
    main()
