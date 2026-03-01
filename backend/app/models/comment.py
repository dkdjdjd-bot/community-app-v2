"""Comment 모델 — 댓글 테이블 및 스키마"""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class CommentBase(SQLModel):
    """댓글 기본 필드"""

    content: str


class Comment(CommentBase, table=True):
    """댓글 DB 테이블 모델"""

    id: int | None = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="user.id", index=True)
    post_id: int = Field(foreign_key="post.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CommentCreate(SQLModel):
    """댓글 생성 요청 스키마"""

    content: str


class CommentUpdate(SQLModel):
    """댓글 수정 요청 스키마"""

    content: str


class CommentResponse(SQLModel):
    """댓글 응답 스키마"""

    id: int
    content: str
    author_id: int
    author_nickname: str = ""
    post_id: int
    created_at: datetime
    updated_at: datetime
