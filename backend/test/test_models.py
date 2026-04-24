import pytest
from pydantic import ValidationError
from app.models import (
    UserCreate,
    UserLogin,
    FormSubmit,
    CouponGrab,
    Token,
)


class TestUserModels:
    """用户模型测试 - 包含边界值和异常"""

    def test_user_create_valid(self):
        user = UserCreate(username="testuser", password="password123")
        assert user.username == "testuser"
        assert user.password == "password123"

    def test_user_create_missing_password(self):
        with pytest.raises(ValidationError):
            UserCreate(username="testuser")

    def test_user_create_missing_username(self):
        with pytest.raises(ValidationError):
            UserCreate(password="password123")

    def test_user_login_valid(self):
        login = UserLogin(username="testuser", password="password123")
        assert login.username == "testuser"
        assert login.password == "password123"

    # 边界值测试
    def test_username_min_length(self):
        """边界值：用户名最短长度（1字符）"""
        user = UserCreate(username="a", password="password123")
        assert user.username == "a"

    def test_username_max_length(self):
        """边界值：用户名最大长度（常见限制 30）"""
        user = UserCreate(username="a" * 30, password="password123")
        assert len(user.username) == 30

    def test_password_min_length(self):
        """边界值：密码最短长度"""
        user = UserCreate(username="testuser", password="123456")
        assert len(user.password) == 6

    def test_empty_username(self):
        """边界值：空用户名（Pydantic 默认允许，需业务层验证）"""
        user = UserCreate(username="", password="password123")
        assert user.username == ""

    def test_empty_password(self):
        """边界值：空密码（Pydantic 默认允许）"""
        user = UserCreate(username="testuser", password="")
        assert user.password == ""

    def test_whitespace_username(self):
        """边界值：用户名包含空格（Pydantic 默认不过滤）"""
        user = UserCreate(username="  test  ", password="password123")
        assert user.username == "  test  "  # 不过滤

    def test_special_characters_username(self):
        """边界值：用户名特殊字符"""
        user = UserCreate(username="user@123", password="password123")
        assert user.username == "user@123"

    def test_numeric_username(self):
        """边界值：纯数字用户名"""
        user = UserCreate(username="12345", password="password123")
        assert user.username == "12345"


class TestFormSubmitModel:
    """表单提交模型测试 - 包含边界值和异常"""

    def test_form_submit_valid(self):
        form = FormSubmit(name="John Doe", contact="john@example.com", note="test note")
        assert form.name == "John Doe"
        assert form.contact == "john@example.com"
        assert form.note == "test note"

    def test_form_submit_without_note(self):
        form = FormSubmit(name="John Doe", contact="john@example.com")
        assert form.note is None

    def test_form_submit_missing_name(self):
        with pytest.raises(ValidationError):
            FormSubmit(contact="john@example.com")

    def test_form_submit_missing_contact(self):
        with pytest.raises(ValidationError):
            FormSubmit(name="John Doe")

    # 边界值测试
    def test_name_min_length(self):
        """边界值：名字最短"""
        form = FormSubmit(name="J", contact="j@j.com")
        assert form.name == "J"

    def test_name_max_length(self):
        """边界值：名字最大长度"""
        form = FormSubmit(name="J" * 100, contact="j@j.com")
        assert len(form.name) == 100

    def test_contact_email_format(self):
        """边界值：各种邮箱格式"""
        form = FormSubmit(name="John", contact="test@test.com")
        assert "@" in form.contact

    def test_contact_invalid_format(self):
        """边界值：无效邮箱格式（Pydantic 默认不验证 Email）"""
        form = FormSubmit(name="John", contact="not-an-email")
        assert form.contact == "not-an-email"  # 默认接受任意字符串

    def test_empty_contact(self):
        """边界值：空联系方式"""
        form = FormSubmit(name="John", contact="")
        assert form.contact == ""

    def test_note_empty_string(self):
        """边界值：空字符串 note（与 None 不同）"""
        form = FormSubmit(name="John", contact="j@j.com", note="")
        assert form.note == ""

    def test_note_max_length(self):
        """边界值：备注最大长度"""
        long_note = "a" * 500
        form = FormSubmit(name="John", contact="j@j.com", note=long_note)
        assert len(form.note) == 500


class TestCouponGrabModel:
    """优惠券模型测试 - 包含边界值和异常"""

    def test_coupon_grab_valid(self):
        grab = CouponGrab(coupon_id=1)
        assert grab.coupon_id == 1

    def test_coupon_grab_invalid_id(self):
        with pytest.raises(ValidationError):
            CouponGrab(coupon_id="invalid")

    # 边界值测试
    def test_coupon_grab_zero_id(self):
        """边界值：ID 为 0"""
        grab = CouponGrab(coupon_id=0)
        assert grab.coupon_id == 0

    def test_coupon_grab_negative_id(self):
        """边界值：负数 ID（Pydantic 默认接受负数整数）"""
        grab = CouponGrab(coupon_id=-1)
        assert grab.coupon_id == -1

    def test_coupon_grab_large_id(self):
        """边界值：大数值 ID"""
        grab = CouponGrab(coupon_id=999999)
        assert grab.coupon_id == 999999

    def test_coupon_grab_float_id(self):
        """异常：浮点数 ID"""
        with pytest.raises(ValidationError):
            CouponGrab(coupon_id=1.5)


class TestTokenModel:
    """Token 模型测试"""

    def test_token_valid(self):
        token = Token(access_token="abc123", token_type="bearer")
        assert token.access_token == "abc123"
        assert token.token_type == "bearer"

    def test_token_empty_access_token(self):
        """边界值：空 access_token"""
        token = Token(access_token="", token_type="bearer")
        assert token.access_token == ""

    def test_token_different_types(self):
        """边界值：不同 token_type"""
        token = Token(access_token="abc123", token_type="macaroon")
        assert token.token_type == "macaroon"
