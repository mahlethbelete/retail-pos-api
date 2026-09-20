import pytest
from fastapi import HTTPException, status

from services import auth_service


def make_payload(**overrides):
    payload = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "username": "jane_cashier",
        "role": "cashier",
        "password": "CorrectPassword123",
    }
    payload.update(overrides)
    return payload


def test_create_user_hashes_password(db_session):
    user = auth_service.create_user(db_session, make_payload())

    assert user.username == "jane_cashier"
    assert user.role == "cashier"
    assert user.password_hash != "CorrectPassword123"
    assert user.is_active is True


def test_create_user_already_registered(db_session):
    auth_service.create_user(db_session, make_payload())

    with pytest.raises(HTTPException) as exc_info:
        auth_service.create_user(db_session, make_payload())

    assert exc_info.value.status_code == 409
    assert "already registered" in exc_info.value.detail


def test_authenticate_success(db_session):
    created = auth_service.create_user(db_session, make_payload())

    user = auth_service.authenticate(db_session, "jane_cashier", "CorrectPassword123")

    assert user.user_id == created.user_id


def test_authenticate_invalid_password(db_session):
    auth_service.create_user(db_session, make_payload())

    with pytest.raises(HTTPException) as exc_info:
        auth_service.authenticate(db_session, "jane_cashier", "WrongPassword")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid username" in exc_info.value.detail


def test_authenticate_unknown_user(db_session):
    with pytest.raises(HTTPException) as exc_info:
        auth_service.authenticate(db_session, "nobody", "CorrectPassword123")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_authenticate_user_inactive(db_session):
    user = auth_service.create_user(db_session, make_payload())
    user.is_active = False
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        auth_service.authenticate(db_session, "jane_cashier", "CorrectPassword123")

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "account is inactive" in exc_info.value.detail


def test_make_login_response(db_session):
    user = auth_service.create_user(db_session, make_payload())

    response = auth_service.make_login_response(user)

    assert response["token_type"] == "bearer"
    assert response["user"] is user
    assert isinstance(response["access_token"], str)


def test_get_user_from_token_round_trip(db_session):
    user = auth_service.create_user(db_session, make_payload())
    token = auth_service.make_login_response(user)["access_token"]

    assert auth_service.get_user_from_token(db_session, token).user_id == user.user_id


def test_get_user_from_token_rejects_garbage(db_session):
    with pytest.raises(HTTPException) as exc_info:
        auth_service.get_user_from_token(db_session, "not-a-token")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED