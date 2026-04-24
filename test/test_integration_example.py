"""
集成测试 - 完整覆盖所有 API
包含：正常流程、异常流程、边界值、认证测试
"""
import requests
import os
import uuid
import pytest

TARGET_URL = os.environ.get("TARGET_URL", "http://localhost:8000")

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def registered_user():
    """注册并登录一个测试用户"""
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    # 注册
    resp = requests.post(f"{TARGET_URL}/auth/register", json={
        "username": username,
        "password": "Test123456"
    })
    assert resp.status_code in (200, 201), f"Register failed: {resp.status_code}"

    # 登录
    resp = requests.post(f"{TARGET_URL}/auth/login", json={
        "username": username,
        "password": "Test123456"
    })
    assert resp.status_code == 200, f"Login failed: {resp.status_code}"
    token = resp.json().get("access_token")
    assert token, "No token returned"
    return {"username": username, "token": token}


@pytest.fixture(scope="module")
def another_user():
    """注册另一个测试用户"""
    username = f"another_{uuid.uuid4().hex[:8]}"
    resp = requests.post(f"{TARGET_URL}/auth/register", json={
        "username": username,
        "password": "Test123456"
    })
    assert resp.status_code in (200, 201)

    resp = requests.post(f"{TARGET_URL}/auth/login", json={
        "username": username,
        "password": "Test123456"
    })
    assert resp.status_code == 200
    token = resp.json().get("access_token")
    return {"username": username, "token": token}


# ============================================================================
# 健康检查
# ============================================================================

def test_health():
    """正常流程：健康检查"""
    response = requests.get(f"{TARGET_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# ============================================================================
# 认证 API - /auth/*
# ============================================================================

class TestAuthRegister:
    """注册 API 测试"""

    def test_register_success(self):
        """正常流程：注册成功"""
        username = f"newuser_{uuid.uuid4().hex[:8]}"
        resp = requests.post(f"{TARGET_URL}/auth/register", json={
            "username": username,
            "password": "Test123456"
        })
        assert resp.status_code in (200, 201)
        assert "message" in resp.json()

    def test_register_duplicate_username(self):
        """异常流程：用户名已存在"""
        username = f"dup_{uuid.uuid4().hex[:8]}"
        # 第一次注册
        requests.post(f"{TARGET_URL}/auth/register", json={
            "username": username,
            "password": "Test123456"
        })
        # 第二次注册同一用户名
        resp = requests.post(f"{TARGET_URL}/auth/register", json={
            "username": username,
            "password": "Test123456"
        })
        assert resp.status_code == 400
        assert "already exists" in resp.json().get("detail", "")

    def test_register_missing_username(self):
        """异常流程：缺少用户名"""
        resp = requests.post(f"{TARGET_URL}/auth/register", json={
            "password": "Test123456"
        })
        assert resp.status_code == 422  # Pydantic 验证失败

    def test_register_missing_password(self):
        """异常流程：缺少密码"""
        resp = requests.post(f"{TARGET_URL}/auth/register", json={
            "username": "testuser"
        })
        assert resp.status_code == 422

    def test_register_empty_body(self):
        """异常流程：空请求体"""
        resp = requests.post(f"{TARGET_URL}/auth/register", json={})
        assert resp.status_code == 422

    def test_register_short_password(self):
        """边界值：密码过短（如少于6位，实际取决于业务逻辑）"""
        username = f"shortpw_{uuid.uuid4().hex[:8]}"
        resp = requests.post(f"{TARGET_URL}/auth/register", json={
            "username": username,
            "password": "123"  # 短密码
        })
        # 业务逻辑决定是 400 还是 201，这里检查实际行为
        assert resp.status_code in (200, 201, 400)


class TestAuthLogin:
    """登录 API 测试"""

    def test_login_success(self, registered_user):
        """正常流程：登录成功"""
        resp = requests.post(f"{TARGET_URL}/auth/login", json={
            "username": registered_user["username"],
            "password": "Test123456"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, registered_user):
        """异常流程：密码错误"""
        resp = requests.post(f"{TARGET_URL}/auth/login", json={
            "username": registered_user["username"],
            "password": "WrongPassword"
        })
        assert resp.status_code == 401
        assert "Invalid credentials" in resp.json().get("detail", "")

    def test_login_nonexistent_user(self):
        """异常流程：用户不存在"""
        resp = requests.post(f"{TARGET_URL}/auth/login", json={
            "username": f"nonexistent_{uuid.uuid4().hex[:8]}",
            "password": "Test123456"
        })
        assert resp.status_code == 401

    def test_login_missing_username(self):
        """异常流程：缺少用户名"""
        resp = requests.post(f"{TARGET_URL}/auth/login", json={
            "password": "Test123456"
        })
        assert resp.status_code == 422

    def test_login_missing_password(self):
        """异常流程：缺少密码"""
        resp = requests.post(f"{TARGET_URL}/auth/login", json={
            "username": "testuser"
        })
        assert resp.status_code == 422


class TestAuthMe:
    """获取当前用户 API 测试"""

    def test_me_success(self, registered_user):
        """正常流程：获取当前用户信息"""
        headers = {"Authorization": f"Bearer {registered_user['token']}"}
        resp = requests.get(f"{TARGET_URL}/auth/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["username"] == registered_user["username"]

    def test_me_no_token(self):
        """异常流程：无 token"""
        resp = requests.get(f"{TARGET_URL}/auth/me")
        assert resp.status_code == 403  # HTTPBearer 默认返回 403

    def test_me_invalid_token(self):
        """异常流程：无效 token"""
        headers = {"Authorization": "Bearer invalid_token"}
        resp = requests.get(f"{TARGET_URL}/auth/me", headers=headers)
        assert resp.status_code == 401

    def test_me_expired_token(self):
        """边界值：伪造的 token"""
        headers = {"Authorization": "Bearer fake.token.here"}
        resp = requests.get(f"{TARGET_URL}/auth/me", headers=headers)
        assert resp.status_code == 401


# ============================================================================
# 表单 API - /form/*
# ============================================================================

class TestFormSubmit:
    """表单提交 API 测试"""

    def test_submit_success(self, registered_user):
        """正常流程：提交表单成功"""
        headers = {"Authorization": f"Bearer {registered_user['token']}"}
        resp = requests.post(f"{TARGET_URL}/form/submit", json={
            "name": "John Doe",
            "contact": "john@example.com",
            "note": "Test note"
        }, headers=headers)
        assert resp.status_code == 200
        assert "message" in resp.json()

    def test_submit_without_note(self, another_user):
        """边界值：不带 note 提交"""
        headers = {"Authorization": f"Bearer {another_user['token']}"}
        resp = requests.post(f"{TARGET_URL}/form/submit", json={
            "name": "Jane Doe",
            "contact": "jane@example.com"
        }, headers=headers)
        assert resp.status_code == 200

    def test_submit_no_auth(self):
        """异常流程：未认证"""
        resp = requests.post(f"{TARGET_URL}/form/submit", json={
            "name": "John Doe",
            "contact": "john@example.com"
        })
        assert resp.status_code == 403

    def test_submit_invalid_token(self):
        """异常流程：无效 token"""
        headers = {"Authorization": "Bearer invalid_token"}
        resp = requests.post(f"{TARGET_URL}/form/submit", json={
            "name": "John Doe",
            "contact": "john@example.com"
        }, headers=headers)
        assert resp.status_code == 401

    def test_submit_missing_name(self, registered_user):
        """异常流程：缺少姓名"""
        headers = {"Authorization": f"Bearer {registered_user['token']}"}
        resp = requests.post(f"{TARGET_URL}/form/submit", json={
            "contact": "john@example.com"
        }, headers=headers)
        assert resp.status_code == 422

    def test_submit_missing_contact(self, registered_user):
        """异常流程：缺少联系方式"""
        headers = {"Authorization": f"Bearer {registered_user['token']}"}
        resp = requests.post(f"{TARGET_URL}/form/submit", json={
            "name": "John Doe"
        }, headers=headers)
        assert resp.status_code == 422

    def test_submit_empty_name(self, registered_user):
        """边界值：姓名为空（Pydantic 默认接受空字符串）"""
        headers = {"Authorization": f"Bearer {registered_user['token']}"}
        resp = requests.post(f"{TARGET_URL}/form/submit", json={
            "name": "",
            "contact": "john@example.com"
        }, headers=headers)
        # Pydantic 默认接受空字符串，业务层未做额外验证
        assert resp.status_code == 200


class TestFormList:
    """表单列表 API 测试"""

    def test_list_success(self, registered_user):
        """正常流程：获取表单列表"""
        headers = {"Authorization": f"Bearer {registered_user['token']}"}
        resp = requests.get(f"{TARGET_URL}/form/list", headers=headers)
        assert resp.status_code == 200
        assert "forms" in resp.json()

    def test_list_no_auth(self):
        """异常流程：未认证"""
        resp = requests.get(f"{TARGET_URL}/form/list")
        assert resp.status_code == 403


# ============================================================================
# 优惠券 API - /coupons/*
# ============================================================================

class TestCouponList:
    """优惠券列表 API 测试"""

    def test_list_success(self, registered_user):
        """正常流程：获取优惠券列表"""
        headers = {"Authorization": f"Bearer {registered_user['token']}"}
        resp = requests.get(f"{TARGET_URL}/coupons/list", headers=headers)
        assert resp.status_code == 200
        assert "coupons" in resp.json()

    def test_list_no_auth(self):
        """正常流程：公开接口，无需认证"""
        resp = requests.get(f"{TARGET_URL}/coupons/list")
        assert resp.status_code == 200

    def test_list_invalid_token(self):
        """正常流程：公开接口，token 不影响结果"""
        headers = {"Authorization": "Bearer invalid_token"}
        resp = requests.get(f"{TARGET_URL}/coupons/list", headers=headers)
        assert resp.status_code == 200


class TestCouponGrab:
    """抢优惠券 API 测试"""

    def test_grab_success(self, registered_user):
        """正常流程：抢优惠券成功"""
        headers = {"Authorization": f"Bearer {registered_user['token']}"}
        # 先获取优惠券列表
        resp = requests.get(f"{TARGET_URL}/coupons/list", headers=headers)
        coupons = resp.json().get("coupons", [])
        if coupons:
            coupon_id = coupons[0]["id"]
            resp = requests.post(f"{TARGET_URL}/coupons/grab", json={
                "coupon_id": coupon_id
            }, headers=headers)
            # 可能是 200 成功，或 400 已领过
            assert resp.status_code in (200, 400)

    def test_grab_no_auth(self):
        """异常流程：未认证"""
        resp = requests.post(f"{TARGET_URL}/coupons/grab", json={
            "coupon_id": 1
        })
        assert resp.status_code == 403

    def test_grab_invalid_token(self):
        """异常流程：无效 token"""
        headers = {"Authorization": "Bearer invalid_token"}
        resp = requests.post(f"{TARGET_URL}/coupons/grab", json={
            "coupon_id": 1
        }, headers=headers)
        assert resp.status_code == 401

    def test_grab_nonexistent_coupon(self, registered_user):
        """异常流程：优惠券不存在"""
        headers = {"Authorization": f"Bearer {registered_user['token']}"}
        resp = requests.post(f"{TARGET_URL}/coupons/grab", json={
            "coupon_id": 99999
        }, headers=headers)
        assert resp.status_code == 404

    def test_grab_already_grabbed(self, another_user):
        """异常流程：重复领取"""
        headers = {"Authorization": f"Bearer {another_user['token']}"}
        # 获取优惠券
        resp = requests.get(f"{TARGET_URL}/coupons/list", headers=headers)
        coupons = resp.json().get("coupons", [])
        if coupons:
            coupon_id = coupons[0]["id"]
            # 第一次抢
            requests.post(f"{TARGET_URL}/coupons/grab", json={
                "coupon_id": coupon_id
            }, headers=headers)
            # 第二次抢
            resp = requests.post(f"{TARGET_URL}/coupons/grab", json={
                "coupon_id": coupon_id
            }, headers=headers)
            assert resp.status_code == 400
            assert "already" in resp.json().get("detail", "").lower()


class TestCouponMy:
    """我的优惠券 API 测试"""

    def test_my_success(self, registered_user):
        """正常流程：获取我的优惠券"""
        headers = {"Authorization": f"Bearer {registered_user['token']}"}
        resp = requests.get(f"{TARGET_URL}/coupons/my", headers=headers)
        assert resp.status_code == 200
        assert "coupons" in resp.json()

    def test_my_no_auth(self):
        """异常流程：未认证"""
        resp = requests.get(f"{TARGET_URL}/coupons/my")
        assert resp.status_code == 403


# ============================================================================
# 查询 API - /query/*
# ============================================================================

class TestQueryForms:
    """查询表单 API 测试"""

    def test_query_forms_success(self, registered_user):
        """正常流程：查询表单"""
        headers = {"Authorization": f"Bearer {registered_user['token']}"}
        resp = requests.get(f"{TARGET_URL}/query/forms", headers=headers)
        assert resp.status_code == 200
        assert "forms" in resp.json()

    def test_query_forms_with_keyword(self, registered_user):
        """边界值：带关键字查询"""
        headers = {"Authorization": f"Bearer {registered_user['token']}"}
        resp = requests.get(f"{TARGET_URL}/query/forms?keyword=test", headers=headers)
        assert resp.status_code == 200

    def test_query_forms_no_auth(self):
        """异常流程：未认证"""
        resp = requests.get(f"{TARGET_URL}/query/forms")
        assert resp.status_code == 403


class TestQueryCoupons:
    """查询优惠券 API 测试"""

    def test_query_coupons_success(self, registered_user):
        """正常流程：查询优惠券"""
        headers = {"Authorization": f"Bearer {registered_user['token']}"}
        resp = requests.get(f"{TARGET_URL}/query/coupons", headers=headers)
        assert resp.status_code == 200
        assert "coupons" in resp.json()

    def test_query_coupons_with_keyword(self, registered_user):
        """边界值：带关键字查询"""
        headers = {"Authorization": f"Bearer {registered_user['token']}"}
        resp = requests.get(f"{TARGET_URL}/query/coupons?keyword=test", headers=headers)
        assert resp.status_code == 200

    def test_query_coupons_no_auth(self):
        """异常流程：未认证"""
        resp = requests.get(f"{TARGET_URL}/query/coupons")
        assert resp.status_code == 403
