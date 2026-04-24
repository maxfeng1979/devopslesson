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


class TestFormSubmitModel:
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


class TestCouponGrabModel:
    def test_coupon_grab_valid(self):
        grab = CouponGrab(coupon_id=1)
        assert grab.coupon_id == 1

    def test_coupon_grab_invalid_id(self):
        with pytest.raises(ValidationError):
            CouponGrab(coupon_id="invalid")


class TestTokenModel:
    def test_token_valid(self):
        token = Token(access_token="abc123", token_type="bearer")
        assert token.access_token == "abc123"
        assert token.token_type == "bearer"
