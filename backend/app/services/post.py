"""게시글 서비스 — CRUD 로직, 페이지네이션, 소프트 삭제"""

import math
from datetime import datetime, timezone

from sqlmodel import Session, col, func, select

from app.models.post import Post, PostCreate, PostListResponse, PostResponse, PostUpdate
from app.models.user import User


def _to_response(post: Post, session: Session) -> PostResponse:
    """Post 모델을 PostResponse로 변환 (작성자 닉네임 포함)"""
    author = session.get(User, post.author_id)
    return PostResponse(
        id=post.id,  # type: ignore
        title=post.title,
        content=post.content,
        author_id=post.author_id,
        author_nickname=author.nickname if author else "",
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


def create_post(session: Session, post_data: PostCreate, author_id: int) -> PostResponse:
    """게시글 생성"""
    post = Post(
        title=post_data.title,
        content=post_data.content,
        author_id=author_id,
    )
    session.add(post)
    session.commit()
    session.refresh(post)
    return _to_response(post, session)


def get_post(session: Session, post_id: int) -> PostResponse | None:
    """게시글 상세 조회 (소프트 삭제된 것 제외)"""
    post = session.get(Post, post_id)
    if not post or post.is_deleted:
        return None
    return _to_response(post, session)


def list_posts(session: Session, page: int = 1, per_page: int = 10) -> PostListResponse:
    """게시글 목록 조회 (페이지네이션, 최신순, 소프트 삭제 제외)"""
    # 전체 개수 (삭제되지 않은 것만)
    count_stmt = select(func.count()).select_from(Post).where(Post.is_deleted == False)  # noqa: E712
    total = session.exec(count_stmt).one()

    # 페이지네이션 적용
    offset = (page - 1) * per_page
    stmt = (
        select(Post)
        .where(Post.is_deleted == False)  # noqa: E712
        .order_by(col(Post.created_at).desc())
        .offset(offset)
        .limit(per_page)
    )
    posts = session.exec(stmt).all()

    items = [_to_response(p, session) for p in posts]
    total_pages = math.ceil(total / per_page) if per_page > 0 else 0

    return PostListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


def update_post(
    session: Session, post_id: int, post_data: PostUpdate, author_id: int
) -> PostResponse | None:
    """게시글 수정 (작성자만 가능). 권한 없으면 'forbidden' 반환"""
    post = session.get(Post, post_id)
    if not post or post.is_deleted:
        return None
    if post.author_id != author_id:
        return "forbidden"  # type: ignore

    if post_data.title is not None:
        post.title = post_data.title
    if post_data.content is not None:
        post.content = post_data.content
    post.updated_at = datetime.now(timezone.utc)

    session.add(post)
    session.commit()
    session.refresh(post)
    return _to_response(post, session)


def delete_post(session: Session, post_id: int, author_id: int) -> str:
    """게시글 소프트 삭제 (작성자만 가능). 결과: 'ok', 'not_found', 'forbidden'"""
    post = session.get(Post, post_id)
    if not post or post.is_deleted:
        return "not_found"
    if post.author_id != author_id:
        return "forbidden"

    post.is_deleted = True
    session.add(post)
    session.commit()
    return "ok"
