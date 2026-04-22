"""Root test configuration.

This conftest MUST run before any `app.*` modules are imported so that:
  1. `DATABASE_URL` is pointed at an in-memory SQLite (prevents the real
     `elara.db` from being touched when `app.main` calls `create_all`).
  2. The heavy `app.pipelines.mark_one` module is stubbed out so that
     importing `app.routers.calls` (which does `from app.pipelines.mark_one
     import bot` at module level) does NOT load pipecat / torch / dotenv
     during unit tests.
"""

from __future__ import annotations

import os
import sys
from typing import Generator
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Pre-import setup (runs at conftest import time, before any `app.*` import)
# ---------------------------------------------------------------------------

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests-only")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("TWILIO_ACCOUNT_SID", "ACtestsid")
os.environ.setdefault("TWILIO_AUTH_TOKEN", "testtoken")
os.environ.setdefault("TWILIO_FROM_NUMBER", "+15555550123")
os.environ.setdefault("LOCAL_SERVER_URL", "https://example.ngrok.app")

# Stub the pipeline module BEFORE anything imports `app.routers.calls`.
_pipeline_stub = MagicMock(name="app.pipelines.mark_one")
_pipeline_stub.bot = MagicMock(name="bot")
sys.modules.setdefault("app.pipelines.mark_one", _pipeline_stub)

# ---------------------------------------------------------------------------
# Now we can safely import the app and its dependencies.
# ---------------------------------------------------------------------------
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.database import Base, get_db  # noqa: E402
from app.dependencies import get_current_user  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402  (renamed to avoid clashing with `app` package)

# Register model modules so all tables are attached to `Base.metadata`.
import app.models.users  # noqa: E402, F401
import app.models.agents  # noqa: E402, F401
import app.models.contacts  # noqa: E402, F401
import app.models.recordings  # noqa: E402, F401


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_user() -> dict:
    """A fake authenticated user dict, mirroring `get_current_user`'s return."""
    return {"username": "testuser", "id": 1}


@pytest.fixture
def mock_db() -> MagicMock:
    """A MagicMock session for unit-testing endpoints.

    Tests configure expected return values per-call, e.g.::

        mock_db.query.return_value.filter.return_value.first.return_value = some_obj
    """
    return MagicMock(spec=Session)


@pytest.fixture
def client(mock_db: MagicMock, mock_user: dict) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with DB + auth dependencies mocked.

    Use this for UNIT tests of endpoints.
    """
    def _override_get_db():
        yield mock_db

    def _override_get_current_user():
        return mock_user

    fastapi_app.dependency_overrides[get_db] = _override_get_db
    fastapi_app.dependency_overrides[get_current_user] = _override_get_current_user
    try:
        with TestClient(fastapi_app) as c:
            yield c
    finally:
        fastapi_app.dependency_overrides.clear()


@pytest.fixture
def unauth_client(mock_db: MagicMock) -> Generator[TestClient, None, None]:
    """TestClient with mocked DB but WITHOUT auth override.

    Useful for testing auth failure paths on protected routes.
    """
    def _override_get_db():
        yield mock_db

    fastapi_app.dependency_overrides[get_db] = _override_get_db
    try:
        with TestClient(fastapi_app) as c:
            yield c
    finally:
        fastapi_app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Integration fixtures: real in-memory SQLite DB
# ---------------------------------------------------------------------------

@pytest.fixture
def test_engine():
    """Fresh in-memory SQLite engine per test.

    `StaticPool` + `check_same_thread=False` keeps the same underlying
    connection across sessions, which is required for :memory: SQLite.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def test_db(test_engine) -> Generator[Session, None, None]:
    """Real SQLAlchemy session bound to the in-memory test engine."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def integration_client(
    test_engine, mock_user: dict
) -> Generator[TestClient, None, None]:
    """TestClient backed by a real in-memory SQLite DB.

    Use when you want to exercise both the endpoint layer AND the DB layer
    end-to-end without hitting any real external services.
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    def _override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def _override_get_current_user():
        return mock_user

    fastapi_app.dependency_overrides[get_db] = _override_get_db
    fastapi_app.dependency_overrides[get_current_user] = _override_get_current_user
    try:
        with TestClient(fastapi_app) as c:
            yield c
    finally:
        fastapi_app.dependency_overrides.clear()
