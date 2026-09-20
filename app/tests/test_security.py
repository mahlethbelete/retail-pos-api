"""Password hashing and JWT helpers in core.security."""

import pytest

from core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_creates_secure_string():
    hashed = hash_password("SuperSecretPassword123!")

    assert hashed != "SuperSecretPassword123!"
    assert isinstance(hashed, str)
    assert len(hashed) > 0


def test_hashing_the_same_password_twice_gives_different_hashes():
    assert hash_password("MySecurePassword") != hash_password("MySecurePassword")


def test_verify_password_correct():
    hashed = hash_password("MySecurePassword")

    assert verify_password("MySecurePassword", hashed) is True


def test_verify_password_incorrect():
    hashed = hash_password("MySecurePassword")

    assert verify_password("WrongPassword123", hashed) is False


@pytest.mark.parametrize("role", ["cashier", "manager", "admin"])
def test_token_round_trip_keeps_subject_and_role(role):
    token = create_access_token(42, role)
    payload = decode_access_token(token)

    assert payload["sub"] == "42"
    assert payload["role"] == role
    assert "exp" in payload


def test_decode_rejects_a_tampered_token():
    token = create_access_token(1, "admin")

    assert decode_access_token(token + "tampered") == {}


def test_decode_rejects_nonsense():
    assert decode_access_token("not-a-token") == {}
