from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path for `from app ...` imports when running plain `pytest`
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import os
import uuid
from typing import Generator
from dotenv import load_dotenv

from app.crud.activity import activity_crud
from app.crud.building import building_crud
from app.crud.organization import organization_crud

load_dotenv()

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists, drop_database
from app.api.deps import get_db
from app.config.db import SqlAlchemyConfig
from app.model.base import Base
from main import app
from app.security.api_key import require_api_key


def _require_base_env() -> None:
    required = [
        "SqlAlchemyDialect",
        "SqlAlchemyDriver",
        "SqlAlchemyHost",
        "SqlAlchemyUser",
        "SqlAlchemyPassword",
    ]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError("Missing required SqlAlchemy* envs: " + ", ".join(missing))


@pytest.fixture(scope="session")
def test_settings_env() -> Generator[None, None, None]:
    _require_base_env()
    # Generate isolated test database name
    test_db = f"test_secunda_{uuid.uuid4().hex[:8]}"

    # Build SQLAlchemy URL for the ephemeral test database
    dialect = os.environ["SqlAlchemyDialect"]
    driver = os.environ.get("SqlAlchemyDriver")
    host = os.environ["SqlAlchemyHost"]
    user = os.environ["SqlAlchemyUser"]
    password = os.environ["SqlAlchemyPassword"]
    port = int(os.environ.get("SqlAlchemyPort", 3306))
    drivername = f"{dialect}+{driver}" if driver else dialect
    db_url = URL.create(
        drivername=drivername,
        username=user,
        password=password,
        host=host,
        port=port,
        database=test_db,
    )

    # Create database if not exists
    if not database_exists(db_url):
        create_database(db_url)

    # Swap environment to point SqlAlchemyConfig at the test database
    prev_db = os.environ.get("SqlAlchemyDatabase")
    os.environ["SqlAlchemyDatabase"] = test_db

    try:
        yield
    finally:
        # Dispose any pooled connections to allow DROP DATABASE
        try:
            SqlAlchemyConfig.engine().dispose()
        except Exception:
            pass
        # Drop the test database
        try:
            if database_exists(db_url):
                drop_database(db_url)
        except Exception:
            pass
        # Restore previous env var if it existed
        if prev_db is not None:
            os.environ["SqlAlchemyDatabase"] = prev_db
        else:
            os.environ.pop("SqlAlchemyDatabase", None)


@pytest.fixture(scope="session")
def engine(test_settings_env: None) -> Engine:
    return SqlAlchemyConfig.engine(pool_pre_ping=True, future=True)


@pytest.fixture(scope="session")
def db_schema(engine: Engine) -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def seed_basic(db_schema: None):
    with SqlAlchemyConfig.session(expire_on_commit=False, autoflush=False, autocommit=False) as db_session:
        b_center = building_crud.create(db_session, {"address": "Center", "latitude": 55.7558, "longitude": 37.6176})
        b_near = building_crud.create(db_session, {"address": "Near", "latitude": 55.7570, "longitude": 37.6150})
        b_far = building_crud.create(db_session, {"address": "Far", "latitude": 56.8380, "longitude": 60.6050})

        a_food = activity_crud.create(db_session, {"name": "Еда", "parent_id": None})
        a_meat = activity_crud.create(db_session, {"name": "Мясная продукция", "parent_id": a_food.id})

        o1 = organization_crud.create(db_session, {"name": "ЕдаМаркет", "building_id": b_center.id, "phones": ["1"]})
        o2 = organization_crud.create(db_session, {"name": "Мясной рай", "building_id": b_near.id, "phones": ["2"]})
        o3 = organization_crud.create(db_session, {"name": "Далеко", "building_id": b_far.id, "phones": ["3"]})

        organization_crud.set_activities(db_session, o1.id, [a_food.id])
        organization_crud.set_activities(db_session, o2.id, [a_meat.id])
        db_session.commit()


@pytest.fixture()
def db_session(db_schema: None) -> Generator[Session, None, None]:
    # Use SqlAlchemyConfig.session() context manager to manage Session lifecycle
    with SqlAlchemyConfig.session(expire_on_commit=False, autoflush=False, autocommit=False) as session:
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise e
        else:
            session.commit()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    # Ensure app uses the same Session as seeding, so data is visible in requests
    def _override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    # Bypass API key check in tests to avoid coupling to env order
    app.dependency_overrides[require_api_key] = lambda: None

    # Override API key dependency to no-op in tests via env key

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
