import pytest

from core.security import hash_password, verify_password

def test_hash_password_creates_secure_string():
    password = "SuperSecretPassword123!"
    
    hashed = hash_password(password)
    
    assert hashed != password
    assert len(hashed) > 0
    assert isinstance(hashed, str)

def test_verify_password_correct():
    password = "MySecurePassword"
    hashed = hash_password(password)
    
    is_valid = verify_password(password, hashed)
    
    assert is_valid is True

def test_verify_password_incorrect():
    password = "MySecurePassword"
    wrong_password = "WrongPassword123"
    hashed = hash_password(password)
    
    is_valid = verify_password(wrong_password, hashed)
    
    assert is_valid is False
