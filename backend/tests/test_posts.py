"""게시글 API 테스트 — CRUD, 페이지네이션, 권한 검증, 소프트 삭제"""

import pytest
from fastapi.testclient import TestClient


# === 헬퍼 함수 ===


def create_user_and_login(client: TestClient, email: str = "user@example.com") -> str:
    """회원가입 후 로그인하여 JWT 토큰 반환"""
    client.post(
        "/auth/register",
        json={"email": email, "password": "password123", "nickname": "유저"},
    )
    resp = client.post(
        "/auth/login",
        json={"email": email, "password": "password123"},
    )
    return resp.json()["access_token"]


def auth_header(token: str) -> dict:
    """인증 헤더 생성"""
    return {"Authorization": f"Bearer {token}"}


# === 게시글 생성 테스트 ===


def test_게시글_생성_성공(client: TestClient):
    """인증된 사용자가 게시글을 생성하면 201 반환"""
    token = create_user_and_login(client)
    response = client.post(
        "/posts",
        json={"title": "첫 번째 게시글", "content": "안녕하세요!"},
        headers=auth_header(token),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "첫 번째 게시글"
    assert data["content"] == "안녕하세요!"
    assert "id" in data
    assert "author_id" in data
    assert "created_at" in data


def test_게시글_생성_인증필요(client: TestClient):
    """인증 없이 게시글 생성 시 401 반환"""
    response = client.post(
        "/posts",
        json={"title": "제목", "content": "내용"},
    )
    assert response.status_code == 401


# === 게시글 목록 조회 테스트 ===


def test_게시글_목록_조회(client: TestClient):
    """게시글 목록을 페이지네이션과 함께 조회"""
    token = create_user_and_login(client)
    # 게시글 3개 생성
    for i in range(3):
        client.post(
            "/posts",
            json={"title": f"게시글 {i+1}", "content": f"내용 {i+1}"},
            headers=auth_header(token),
        )

    response = client.get("/posts")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert "page" in data
    assert "per_page" in data
    assert "total_pages" in data


def test_게시글_목록_페이지네이션(client: TestClient):
    """페이지네이션 파라미터로 게시글 목록 조회"""
    token = create_user_and_login(client)
    # 게시글 5개 생성
    for i in range(5):
        client.post(
            "/posts",
            json={"title": f"게시글 {i+1}", "content": f"내용 {i+1}"},
            headers=auth_header(token),
        )

    # 2개씩, 1페이지
    response = client.get("/posts?page=1&per_page=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["per_page"] == 2
    assert data["total_pages"] == 3


def test_게시글_목록_인증불필요(client: TestClient):
    """게시글 목록은 인증 없이도 조회 가능"""
    response = client.get("/posts")
    assert response.status_code == 200


# === 게시글 상세 조회 테스트 ===


def test_게시글_상세_조회(client: TestClient):
    """게시글 ID로 상세 조회"""
    token = create_user_and_login(client)
    create_resp = client.post(
        "/posts",
        json={"title": "상세 조회 테스트", "content": "상세 내용"},
        headers=auth_header(token),
    )
    post_id = create_resp.json()["id"]

    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "상세 조회 테스트"
    assert data["content"] == "상세 내용"


def test_존재하지않는_게시글_조회(client: TestClient):
    """존재하지 않는 게시글 조회 시 404 반환"""
    response = client.get("/posts/9999")
    assert response.status_code == 404


# === 게시글 수정 테스트 ===


def test_게시글_수정_성공(client: TestClient):
    """작성자가 게시글을 수정하면 200 반환"""
    token = create_user_and_login(client)
    create_resp = client.post(
        "/posts",
        json={"title": "원본 제목", "content": "원본 내용"},
        headers=auth_header(token),
    )
    post_id = create_resp.json()["id"]

    response = client.put(
        f"/posts/{post_id}",
        json={"title": "수정된 제목", "content": "수정된 내용"},
        headers=auth_header(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "수정된 제목"
    assert data["content"] == "수정된 내용"


def test_게시글_수정_권한없음(client: TestClient):
    """다른 사용자의 게시글 수정 시 403 반환"""
    token1 = create_user_and_login(client, "author@example.com")
    token2 = create_user_and_login(client, "other@example.com")

    create_resp = client.post(
        "/posts",
        json={"title": "제목", "content": "내용"},
        headers=auth_header(token1),
    )
    post_id = create_resp.json()["id"]

    response = client.put(
        f"/posts/{post_id}",
        json={"title": "수정 시도"},
        headers=auth_header(token2),
    )
    assert response.status_code == 403


def test_게시글_수정_인증필요(client: TestClient):
    """인증 없이 게시글 수정 시 401 반환"""
    response = client.put(
        "/posts/1",
        json={"title": "수정 시도"},
    )
    assert response.status_code == 401


# === 게시글 삭제 테스트 ===


def test_게시글_삭제_성공(client: TestClient):
    """작성자가 게시글을 삭제하면 소프트 삭제 후 200 반환"""
    token = create_user_and_login(client)
    create_resp = client.post(
        "/posts",
        json={"title": "삭제할 게시글", "content": "삭제 테스트"},
        headers=auth_header(token),
    )
    post_id = create_resp.json()["id"]

    response = client.delete(f"/posts/{post_id}", headers=auth_header(token))
    assert response.status_code == 200

    # 삭제된 게시글은 조회 불가
    get_resp = client.get(f"/posts/{post_id}")
    assert get_resp.status_code == 404


def test_게시글_삭제_권한없음(client: TestClient):
    """다른 사용자의 게시글 삭제 시 403 반환"""
    token1 = create_user_and_login(client, "author2@example.com")
    token2 = create_user_and_login(client, "other2@example.com")

    create_resp = client.post(
        "/posts",
        json={"title": "제목", "content": "내용"},
        headers=auth_header(token1),
    )
    post_id = create_resp.json()["id"]

    response = client.delete(f"/posts/{post_id}", headers=auth_header(token2))
    assert response.status_code == 403


def test_게시글_삭제후_목록에서_제외(client: TestClient):
    """소프트 삭제된 게시글은 목록에서 제외"""
    token = create_user_and_login(client)
    # 게시글 2개 생성
    resp1 = client.post(
        "/posts",
        json={"title": "게시글 1", "content": "내용 1"},
        headers=auth_header(token),
    )
    client.post(
        "/posts",
        json={"title": "게시글 2", "content": "내용 2"},
        headers=auth_header(token),
    )
    post_id = resp1.json()["id"]

    # 1개 삭제
    client.delete(f"/posts/{post_id}", headers=auth_header(token))

    # 목록 조회 시 1개만 나와야 함
    response = client.get("/posts")
    assert response.json()["total"] == 1
