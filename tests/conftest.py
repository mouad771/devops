"""Fixtures de test : base SQLite en mémoire et client HTTP authentifié."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.seed import seed_admin


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    seed_admin(session)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _token(client: TestClient, email: str, password: str) -> str:
    res = client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


@pytest.fixture()
def admin_headers(client):
    token = _token(client, "admin@ecole.ma", "admin1234")
    return {"Authorization": f"Bearer {token}"}
