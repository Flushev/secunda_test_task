from __future__ import annotations

from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.crud.building import building_crud


def test_list_buildings(client: TestClient, db_session: Session):
    headers = {"X-API-Key": "test-key"}

    building_crud.create(db_session, {"address": "Addr", "latitude": 55.0, "longitude": 37.0})

    r = client.get("/api/v1/buildings", headers=headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
