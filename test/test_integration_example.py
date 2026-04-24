"""
集成测试脚本示例
用于测试 DevOps Lesson 系统的 API 功能
"""
import requests
import os
import uuid
import pytest

TARGET_URL = os.environ.get("TARGET_URL", "http://localhost:8000")

@pytest.fixture(scope="module")
def auth_token():
    """获取认证令牌的 fixture"""
    # 注册新用户
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    resp = requests.post(f"{TARGET_URL}/api/auth/register", json={
        "username": username,
        "password": "test123456"
    })
    assert resp.status_code == 200, f"Register failed: {resp.status_code}"
    
    # 登录获取令牌
    resp = requests.post(f"{TARGET_URL}/api/auth/login", json={
        "username": username,
        "password": "test123456"
    })
    assert resp.status_code == 200, f"Login failed: {resp.status_code}"
    token = resp.json().get("access_token")
    assert token, "No token returned"
    print(f"[PASS] Login successful, token: {token[:20]}...")
    return token

def test_health():
    """测试健康检查接口"""
    response = requests.get(f"{TARGET_URL}/health")
    assert response.status_code == 200, f"Health check failed: {response.status_code}"
    print(f"[PASS] Health check: {response.json()}")

def test_form_submit(auth_token):
    """测试表单提交"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = requests.post(f"{TARGET_URL}/api/form/submit", json={
        "name": "Test User",
        "contact": "test@example.com",
        "note": "Test submission"
    }, headers=headers)
    assert resp.status_code == 200, f"Form submit failed: {resp.status_code}"
    print(f"[PASS] Form submitted: {resp.json()}")

def test_coupons(auth_token):
    """测试优惠券功能"""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 获取优惠券列表
    resp = requests.get(f"{TARGET_URL}/api/coupons/list", headers=headers)
    assert resp.status_code == 200, f"Coupon list failed: {resp.status_code}"
    coupons = resp.json()
    print(f"[PASS] Found {len(coupons)} coupons")

    # 尝试抢优惠券
    if coupons:
        resp = requests.post(f"{TARGET_URL}/api/coupons/grab", json={
            "coupon_id": coupons[0]["id"]
        }, headers=headers)
        print(f"[PASS] Grab coupon response: {resp.status_code} - {resp.json()}")
