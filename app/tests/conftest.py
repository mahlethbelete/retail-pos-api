"""Shared pytest fixtures.

The whole suite runs against an in memory SQLite database so it never
touches the PostgreSQL development database. DATABASE_URL is set before
`database` is imported so the app engine is also pointed at SQLite.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite://"
os.environ.setdefault("JWT_SECRET", "test-secret-key-that-is-long-enough-32b")

from database import Base, get_db  # noqa: E402
from main import app  # noqa: E402

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine)


# ---------------------------------------------------------------------------
# database and client
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def setup_database():
    """Fresh schema for every test, dropped afterwards."""
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
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# users and authentication
# ---------------------------------------------------------------------------


def login(client, username, password):
    response = client.post(
        "/auth/login", data={"username": username, "password": password}
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def admin_user(client):
    """First registered account, promoted to admin by the bootstrap rule."""
    payload = {
        "first_name": "Test",
        "last_name": "Admin",
        "email": "admin@example.com",
        "username": "testadmin",
        "password": "testpass123",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201, response.text
    payload["user_id"] = response.json()["user_id"]
    return payload


@pytest.fixture
def auth_headers(client, admin_user):
    return login(client, admin_user["username"], admin_user["password"])


@pytest.fixture
def manager_user(client, auth_headers):
    payload = {
        "first_name": "Test",
        "last_name": "Manager",
        "email": "manager@example.com",
        "username": "testmanager",
        "password": "testpass123",
        "role": "manager",
    }
    response = client.post("/auth/users", json=payload, headers=auth_headers)
    assert response.status_code == 201, response.text
    payload["user_id"] = response.json()["user_id"]
    return payload


@pytest.fixture
def manager_headers(client, manager_user):
    return login(client, manager_user["username"], manager_user["password"])


@pytest.fixture
def cashier_user(client, auth_headers):
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
    payload["user_id"] = response.json()["user_id"]
    return payload


@pytest.fixture
def cashier_headers(client, cashier_user):
    return login(client, cashier_user["username"], cashier_user["password"])


# ---------------------------------------------------------------------------
# entity factories
# ---------------------------------------------------------------------------


@pytest.fixture
def category(client, auth_headers):
    response = client.post(
        "/categories/",
        json={"name": "Beverages", "description": "Sodas, juice and water"},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def supplier(client, auth_headers):
    response = client.post(
        "/suppliers/",
        json={
            "name": "Nairobi Distributors Ltd",
            "phone": "0722000111",
            "email": "sales@nairobidist.co.ke",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def product(client, auth_headers, category, supplier):
    response = client.post(
        "/products/",
        json={
            "name": "Coca Cola 500ml",
            "description": "Chilled soft drink",
            "unit_price": "60.00",
            "cost_price": "45.00",
            "quantity_in_stock": 120,
            "reorder_level": 20,
            "category_id": category["category_id"],
            "supplier_id": supplier["supplier_id"],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def customer(client, auth_headers):
    response = client.post(
        "/customers/",
        json={
            "first_name": "Wanjiru",
            "last_name": "Kamau",
            "email": "wanjiru@example.co.ke",
            "phone": "0733444555",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def sale(client, auth_headers, admin_user, customer):
    response = client.post(
        "/sales/",
        json={
            "customer_id": customer["customer_id"],
            "user_id": admin_user["user_id"],
            "subtotal": "120.00",
            "tax_amount": "19.20",
            "total": "139.20",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()
