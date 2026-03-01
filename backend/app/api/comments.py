"""댓글 라우터 — 게시글별 댓글 CRUD"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.database import get_session
from app.models.comment import CommentCreate, CommentResponse, CommentUpdate
from app.models.user import User
from app.services.comment import (
    create_comment,
    delete_comment,
    list_comments,
    update_comment,
)

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["댓글"])


@router.post("", response_model=CommentResponse, status_code=201)
def create(
    post_id: int,
    comment_data: CommentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """댓글 생성 (인증 필요)"""
    result = create_comment(session, post_id, comment_data, current_user.id)  # type: ignore
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다",
        )
    return result


@router.get("", response_model=list[CommentResponse])
def list_all(post_id: int, session: Session = Depends(get_session)):
    """게시글의 댓글 목록 조회 (인증 불필요)"""
    return list_comments(session, post_id)


@router.put("/{comment_id}", response_model=CommentResponse)
def update(
    post_id: int,
    comment_id: int,
    comment_data: CommentUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """댓글 수정 (작성자만 가능)"""
    result = update_comment(session, comment_id, comment_data, current_user.id)  # type: ignore
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다",
        )
    if result == "forbidden":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="수정 권한이 없습니다",
        )
    return result


@router.delete("/{comment_id}")
def delete(
    post_id: int,
    comment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """댓글 삭제 (작성자만 가능)"""
    result = delete_comment(session, comment_id, current_user.id)  # type: ignore
    if result == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다",
        )
    if result == "forbidden":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="삭제 권한이 없습니다",
        )
    return {"message": "댓글이 삭제되었습니다"}
