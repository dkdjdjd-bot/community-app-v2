"""댓글 API 테스트 — CRUD, 권한 검증, 존재하지 않는 게시글"""

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


def create_post(client: TestClient, token: str) -> int:
    """게시글 생성 후 ID 반환"""
    resp = client.post(
        "/posts",
        json={"title": "테스트 게시글", "content": "내용"},
        headers=auth_header(token),
    )
    return resp.json()["id"]


# === 댓글 생성 테스트 ===


def test_댓글_생성_성공(client: TestClient):
    """인증된 사용자가 댓글을 생성하면 201 반환"""
    token = create_user_and_login(client)
    post_id = create_post(client, token)

    response = client.post(
        f"/posts/{post_id}/comments",
        json={"content": "첫 번째 댓글입니다"},
        headers=auth_header(token),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "첫 번째 댓글입니다"
    assert data["post_id"] == post_id
    assert "id" in data
    assert "author_id" in data
    assert "created_at" in data


def test_댓글_생성_인증필요(client: TestClient):
    """인증 없이 댓글 생성 시 401 반환"""
    token = create_user_and_login(client)
    post_id = create_post(client, token)

    response = client.post(
        f"/posts/{post_id}/comments",
        json={"content": "댓글"},
    )
    assert response.status_code == 401


def test_댓글_생성_존재하지않는_게시글(client: TestClient):
    """존재하지 않는 게시글에 댓글 생성 시 404 반환"""
    token = create_user_and_login(client)
    response = client.post(
        "/posts/9999/comments",
        json={"content": "댓글"},
        headers=auth_header(token),
    )
    assert response.status_code == 404


# === 댓글 목록 조회 테스트 ===


def test_댓글_목록_조회(client: TestClient):
    """게시글의 댓글 목록 조회"""
    token = create_user_and_login(client)
    post_id = create_post(client, token)

    # 댓글 3개 생성
    for i in range(3):
        client.post(
            f"/posts/{post_id}/comments",
            json={"content": f"댓글 {i+1}"},
            headers=auth_header(token),
        )

    response = client.get(f"/posts/{post_id}/comments")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_댓글_목록_인증불필요(client: TestClient):
    """댓글 목록은 인증 없이도 조회 가능"""
    token = create_user_and_login(client)
    post_id = create_post(client, token)

    response = client.get(f"/posts/{post_id}/comments")
    assert response.status_code == 200


# === 댓글 수정 테스트 ===


def test_댓글_수정_성공(client: TestClient):
    """작성자가 댓글을 수정하면 200 반환"""
    token = create_user_and_login(client)
    post_id = create_post(client, token)

    create_resp = client.post(
        f"/posts/{post_id}/comments",
        json={"content": "원본 댓글"},
        headers=auth_header(token),
    )
    comment_id = create_resp.json()["id"]

    response = client.put(
        f"/posts/{post_id}/comments/{comment_id}",
        json={"content": "수정된 댓글"},
        headers=auth_header(token),
    )
    assert response.status_code == 200
    assert response.json()["content"] == "수정된 댓글"


def test_댓글_수정_권한없음(client: TestClient):
    """다른 사용자의 댓글 수정 시 403 반환"""
    token1 = create_user_and_login(client, "author@example.com")
    token2 = create_user_and_login(client, "other@example.com")
    post_id = create_post(client, token1)

    create_resp = client.post(
        f"/posts/{post_id}/comments",
        json={"content": "원본"},
        headers=auth_header(token1),
    )
    comment_id = create_resp.json()["id"]

    response = client.put(
        f"/posts/{post_id}/comments/{comment_id}",
        json={"content": "수정 시도"},
        headers=auth_header(token2),
    )
    assert response.status_code == 403


def test_댓글_수정_인증필요(client: TestClient):
    """인증 없이 댓글 수정 시 401 반환"""
    response = client.put(
        "/posts/1/comments/1",
        json={"content": "수정 시도"},
    )
    assert response.status_code == 401


# === 댓글 삭제 테스트 ===


def test_댓글_삭제_성공(client: TestClient):
    """작성자가 댓글을 삭제하면 200 반환"""
    token = create_user_and_login(client)
    post_id = create_post(client, token)

    create_resp = client.post(
        f"/posts/{post_id}/comments",
        json={"content": "삭제할 댓글"},
        headers=auth_header(token),
    )
    comment_id = create_resp.json()["id"]

    response = client.delete(
        f"/posts/{post_id}/comments/{comment_id}",
        headers=auth_header(token),
    )
    assert response.status_code == 200

    # 삭제 후 목록에서 제외 확인
    list_resp = client.get(f"/posts/{post_id}/comments")
    assert len(list_resp.json()) == 0


def test_댓글_삭제_권한없음(client: TestClient):
    """다른 사용자의 댓글 삭제 시 403 반환"""
    token1 = create_user_and_login(client, "author2@example.com")
    token2 = create_user_and_login(client, "other2@example.com")
    post_id = create_post(client, token1)

    create_resp = client.post(
        f"/posts/{post_id}/comments",
        json={"content": "댓글"},
        headers=auth_header(token1),
    )
    comment_id = create_resp.json()["id"]

    response = client.delete(
        f"/posts/{post_id}/comments/{comment_id}",
        headers=auth_header(token2),
    )
    assert response.status_code == 403


def test_삭제된_게시글에_댓글_생성_불가(client: TestClient):
    """소프트 삭제된 게시글에 댓글 생성 시 404 반환"""
    token = create_user_and_login(client)
    post_id = create_post(client, token)

    # 게시글 삭제
    client.delete(f"/posts/{post_id}", headers=auth_header(token))

    # 삭제된 게시글에 댓글 시도
    response = client.post(
        f"/posts/{post_id}/comments",
        json={"content": "댓글 시도"},
        headers=auth_header(token),
    )
    assert response.status_code == 404
