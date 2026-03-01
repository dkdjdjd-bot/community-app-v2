"""인증 API 테스트 — 회원가입, 로그인, 중복이메일, 잘못된비밀번호, 토큰검증"""

import pytest
from fastapi.testclient import TestClient


# === 회원가입 테스트 ===


def test_회원가입_성공(client: TestClient):
    """유효한 정보로 회원가입 시 201 반환"""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "nickname": "테스트유저",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["nickname"] == "테스트유저"
    assert "id" in data
    assert "hashed_password" not in data  # 비밀번호 해시 노출 금지


def test_회원가입_중복이메일(client: TestClient):
    """이미 등록된 이메일로 가입 시 409 반환"""
    user_data = {
        "email": "dup@example.com",
        "password": "password123",
        "nickname": "유저1",
    }
    client.post("/auth/register", json=user_data)
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 409


def test_회원가입_짧은비밀번호(client: TestClient):
    """8자 미만 비밀번호로 가입 시 422 반환"""
    response = client.post(
        "/auth/register",
        json={
            "email": "short@example.com",
            "password": "short",
            "nickname": "유저",
        },
    )
    assert response.status_code == 422


# === 로그인 테스트 ===


def test_로그인_성공(client: TestClient):
    """유효한 자격 증명으로 로그인 시 JWT 토큰 반환"""
    # 먼저 회원가입
    client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "password123",
            "nickname": "로그인유저",
        },
    )
    # 로그인
    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_로그인_존재하지않는이메일(client: TestClient):
    """등록되지 않은 이메일로 로그인 시 401 반환"""
    response = client.post(
        "/auth/login",
        json={"email": "notexist@example.com", "password": "password123"},
    )
    assert response.status_code == 401


def test_로그인_잘못된비밀번호(client: TestClient):
    """틀린 비밀번호로 로그인 시 401 반환"""
    client.post(
        "/auth/register",
        json={
            "email": "wrong@example.com",
            "password": "password123",
            "nickname": "유저",
        },
    )
    response = client.post(
        "/auth/login",
        json={"email": "wrong@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


# === 토큰 검증 테스트 ===


def test_인증된_사용자_정보조회(client: TestClient):
    """유효한 JWT 토큰으로 현재 사용자 정보 조회"""
    # 회원가입 + 로그인
    client.post(
        "/auth/register",
        json={
            "email": "me@example.com",
            "password": "password123",
            "nickname": "나",
        },
    )
    login_resp = client.post(
        "/auth/login",
        json={"email": "me@example.com", "password": "password123"},
    )
    token = login_resp.json()["access_token"]

    # 사용자 정보 조회
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["nickname"] == "나"


def test_인증없이_보호된_엔드포인트_접근(client: TestClient):
    """토큰 없이 보호된 엔드포인트 접근 시 401 반환"""
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_잘못된_토큰으로_접근(client: TestClient):
    """유효하지 않은 토큰으로 접근 시 401 반환"""
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token-here"},
    )
    assert response.status_code == 401
