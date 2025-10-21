from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_search_by_activity_name(client: TestClient, db_session: Session):
    headers = {"X-API-Key": "test-key"}
    r = client.get("/api/v1/organizations/search", params={"activity_name": "еда"}, headers=headers)
    assert r.status_code == 200
    names = {x["name"] for x in r.json()}
    assert {"ЕдаМаркет", "Мясной рай"}.issubset(names)


def test_filter_endpoint(client: TestClient, db_session: Session):
    headers = {"X-API-Key": "test-key"}
    r = client.post("/api/v1/organizations/filter", json={"activity_name": "мясная продукция"}, headers=headers)
    assert r.status_code == 200
    names = {x["name"] for x in r.json()}
    assert "Мясной рай" in names


def test_nearby_radius(client: TestClient, db_session: Session):
    headers = {"X-API-Key": "test-key"}
    r = client.get(
        "/api/v1/organizations/nearby/radius",
        params={"center_lat": 55.7558, "center_lon": 37.6176, "radius": 300},
        headers=headers,
    )
    assert r.status_code == 200
    names = {x["name"] for x in r.json()}
    assert {"ЕдаМаркет", "Мясной рай"}.issubset(names)


def test_nearby_square(client: TestClient, db_session: Session):
    headers = {"X-API-Key": "test-key"}
    r = client.get(
        "/api/v1/organizations/nearby/square",
        params={"lat_min": 55.75, "lat_max": 55.76, "lon_min": 37.61, "lon_max": 37.62},
        headers=headers,
    )
    assert r.status_code == 200
    names = {x["name"] for x in r.json()}
    assert {"ЕдаМаркет", "Мясной рай"}.issubset(names)
