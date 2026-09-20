import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite://"

from database import Base, get_db  # noqa: E402
from main import app  # noqa: E402

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(client):
    payload = {
        "first_name": "Test",
        "last_name": "Admin",
        "email": "admin@example.com",
        "username": "testadmin",
        "password": "testpass123",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201, response.text
    return payload


@pytest.fixture
def auth_headers(client, admin_user):
    response = client.post(
        "/auth/login",
        data={"username": admin_user["username"], "password": admin_user["password"]},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def cashier_headers(client, auth_headers):
    payload = {
        "first_name": "Test",
        "last_name": "Cashier",
        "email": "cashier@example.com",
        "username": "testcashier",
        "password": "testpass123",
        "role": "cashier",
    }
    response = client.post("/auth/users", json=payload, headers=auth_headers)
    assert response.status_code == 201, response.text

    response = client.post(
        "/auth/login",
        data={"username": payload["username"], "password": payload["password"]},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}