from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_update_list_activity(client: TestClient):
    headers = {"X-API-Key": "test-key"}

    # create
    r = client.post("/api/v1/activities", json={"name": "A", "parent_id": None}, headers=headers)
    assert r.status_code == 200
    a = r.json()

    # update
    r = client.put(f"/api/v1/activities/{a['id']}", json={"name": "A2"}, headers=headers)
    assert r.status_code == 200

    # list
    r = client.get("/api/v1/activities", headers=headers)
    assert r.status_code == 200
    assert any(x["id"] == a["id"] for x in r.json())


def test_activity_nesting_depth_enforced(client: TestClient):
    headers = {"X-API-Key": "test-key"}

    # Level 1 (root)
    r = client.post("/api/v1/activities", json={"name": "L1", "parent_id": None}, headers=headers)
    assert r.status_code == 200
    l1 = r.json()["id"]

    # Level 2
    r = client.post("/api/v1/activities", json={"name": "L2", "parent_id": l1}, headers=headers)
    assert r.status_code == 200
    l2 = r.json()["id"]

    # Level 3 (MAX_DEPTH)
    r = client.post("/api/v1/activities", json={"name": "L3", "parent_id": l2}, headers=headers)
    assert r.status_code == 200
    l3 = r.json()["id"]

    # Level 4 should fail with 400 (exceeds MAX_DEPTH)
    r = client.post("/api/v1/activities", json={"name": "L4", "parent_id": l3}, headers=headers)
    assert r.status_code == 400
