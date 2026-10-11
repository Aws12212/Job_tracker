import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models  # noqa: F401  registers the tables on Base
from database import Base
from deps import get_db
from main import app


@pytest.fixture
def client():
    # Fresh in-memory SQLite database for every test, so tests never touch Postgres
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def make_user(client):
    # Signs up and logs in a user, returning headers that carry their token
    def _make_user(email="user@example.com", password="testpass123"):
        client.post("/auth/signup", json={"email": email, "password": password})
        res = client.post("/auth/login", data={"username": email, "password": password})
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    return _make_user


@pytest.fixture
def auth(make_user):
    return make_user()
