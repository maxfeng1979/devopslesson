import pytest
from datetime import timedelta
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
)


class TestPasswordHashing:
    def test_hash_password(self):
        password = "test_password_123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_correct_password(self):
        password = "test_password_123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        password = "test_password_123"
        hashed = get_password_hash(password)
        assert verify_password("wrong_password", hashed) is False

    def test_different_passwords_different_hashes(self):
        hash1 = get_password_hash("password1")
        hash2 = get_password_hash("password2")
        assert hash1 != hash2


class TestJWTToken:
    def test_create_access_token(self):
        token = create_access_token({"sub": "testuser"})
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        token = create_access_token({"sub": "testuser"})
        username = decode_token(token)
        assert username == "testuser"

    def test_decode_invalid_token(self):
        username = decode_token("invalid.token.here")
        assert username is None

    def test_token_with_custom_expiry(self):
        token = create_access_token(
            {"sub": "testuser"},
            expires_delta=timedelta(hours=1)
        )
        username = decode_token(token)
        assert username == "testuser"
