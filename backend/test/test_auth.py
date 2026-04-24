import pytest
from datetime import timedelta
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
)


class TestPasswordHashing:
    """密码哈希测试 - 包含边界值和异常"""

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

    # 边界值测试
    def test_empty_password(self):
        """边界值：空密码"""
        hashed = get_password_hash("")
        assert len(hashed) > 0
        assert verify_password("", hashed) is True

    def test_very_long_password(self):
        """边界值：超长密码（72字符 bcrypt 限制）"""
        long_password = "a" * 72
        hashed = get_password_hash(long_password)
        assert verify_password(long_password, hashed) is True

    def test_unicode_password(self):
        """边界值：Unicode 字符"""
        password = "测试密码123中文"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_special_characters_password(self):
        """边界值：特殊字符"""
        password = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True


class TestJWTToken:
    """JWT Token 测试 - 包含异常和边界"""

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
        """异常：无效 token"""
        username = decode_token("invalid.token.here")
        assert username is None

    def test_token_with_custom_expiry(self):
        token = create_access_token(
            {"sub": "testuser"},
            expires_delta=timedelta(hours=1)
        )
        username = decode_token(token)
        assert username == "testuser"

    def test_token_with_expired_expiry(self):
        """边界值：已过期的 token"""
        token = create_access_token(
            {"sub": "testuser"},
            expires_delta=timedelta(seconds=-1)  # 已过期
        )
        username = decode_token(token)
        assert username is None

    def test_token_missing_sub(self):
        """异常：token 没有 sub 字段"""
        token = create_access_token({"other": "value"})
        username = decode_token(token)
        assert username is None

    def test_decode_empty_token(self):
        """异常：空 token"""
        username = decode_token("")
        assert username is None

    def test_decode_tampered_token(self):
        """异常：篡改的 token（修改 payload）"""
        token = create_access_token({"sub": "testuser"})
        # 篡改 token（改动最后一个字符）
        tampered = token[:-1] + ("x" if token[-1] != "x" else "y")
        username = decode_token(tampered)
        assert username is None
