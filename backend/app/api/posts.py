"""게시글 라우터 — CRUD + 페이지네이션"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.database import get_session
from app.models.post import PostCreate, PostListResponse, PostResponse, PostUpdate
from app.models.user import User
from app.services.post import create_post, delete_post, get_post, list_posts, update_post

router = APIRouter(prefix="/posts", tags=["게시글"])


@router.post("", response_model=PostResponse, status_code=201)
def create(
    post_data: PostCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """게시글 생성 (인증 필요)"""
    return create_post(session, post_data, current_user.id)  # type: ignore


@router.get("", response_model=PostListResponse)
def list_all(
    page: int = Query(1, ge=1, description="페이지 번호"),
    per_page: int = Query(10, ge=1, le=100, description="페이지당 게시글 수"),
    session: Session = Depends(get_session),
):
    """게시글 목록 조회 (인증 불필요, 페이지네이션)"""
    return list_posts(session, page, per_page)


@router.get("/{post_id}", response_model=PostResponse)
def get_one(post_id: int, session: Session = Depends(get_session)):
    """게시글 상세 조회 (인증 불필요)"""
    post = get_post(session, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다")
    return post


@router.put("/{post_id}", response_model=PostResponse)
def update(
    post_id: int,
    post_data: PostUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """게시글 수정 (작성자만 가능)"""
    result = update_post(session, post_id, post_data, current_user.id)  # type: ignore
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다")
    if result == "forbidden":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="수정 권한이 없습니다")
    return result


@router.delete("/{post_id}")
def delete(
    post_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """게시글 삭제 — 소프트 삭제 (작성자만 가능)"""
    result = delete_post(session, post_id, current_user.id)  # type: ignore
    if result == "not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다")
    if result == "forbidden":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="삭제 권한이 없습니다")
    return {"message": "게시글이 삭제되었습니다"}
