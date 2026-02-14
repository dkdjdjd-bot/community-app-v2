"""댓글 서비스 — CRUD 로직, 권한 확인"""

from datetime import datetime, timezone

from sqlmodel import Session, col, select

from app.models.comment import Comment, CommentCreate, CommentResponse, CommentUpdate
from app.models.post import Post
from app.models.user import User


def _to_response(comment: Comment, session: Session) -> CommentResponse:
    """Comment 모델을 CommentResponse로 변환 (작성자 닉네임 포함)"""
    author = session.get(User, comment.author_id)
    return CommentResponse(
        id=comment.id,  # type: ignore
        content=comment.content,
        author_id=comment.author_id,
        author_nickname=author.nickname if author else "",
        post_id=comment.post_id,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


def _get_post_or_none(session: Session, post_id: int) -> Post | None:
    """게시글 존재 및 삭제 여부 확인"""
    post = session.get(Post, post_id)
    if not post or post.is_deleted:
        return None
    return post


def create_comment(
    session: Session, post_id: int, comment_data: CommentCreate, author_id: int
) -> CommentResponse | None:
    """댓글 생성 (게시글 존재 확인). 게시글 없으면 None 반환"""
    if not _get_post_or_none(session, post_id):
        return None

    comment = Comment(
        content=comment_data.content,
        author_id=author_id,
        post_id=post_id,
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return _to_response(comment, session)


def list_comments(session: Session, post_id: int) -> list[CommentResponse]:
    """게시글의 댓글 목록 조회 (작성 시간순)"""
    stmt = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(col(Comment.created_at).asc())
    )
    comments = session.exec(stmt).all()
    return [_to_response(c, session) for c in comments]


def update_comment(
    session: Session, comment_id: int, comment_data: CommentUpdate, author_id: int
) -> CommentResponse | str | None:
    """댓글 수정. 결과: CommentResponse, 'forbidden', None(not found)"""
    comment = session.get(Comment, comment_id)
    if not comment:
        return None
    if comment.author_id != author_id:
        return "forbidden"

    comment.content = comment_data.content
    comment.updated_at = datetime.now(timezone.utc)
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return _to_response(comment, session)


def delete_comment(session: Session, comment_id: int, author_id: int) -> str:
    """댓글 삭제. 결과: 'ok', 'not_found', 'forbidden'"""
    comment = session.get(Comment, comment_id)
    if not comment:
        return "not_found"
    if comment.author_id != author_id:
        return "forbidden"

    session.delete(comment)
    session.commit()
    return "ok"
