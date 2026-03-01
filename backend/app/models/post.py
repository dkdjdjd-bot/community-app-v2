"""Post 모델 — 게시글 테이블 및 스키마"""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class PostBase(SQLModel):
    """게시글 기본 필드"""

    title: str = Field(max_length=200)
    content: str


class Post(PostBase, table=True):
    """게시글 DB 테이블 모델"""

    id: int | None = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_deleted: bool = Field(default=False)


class PostCreate(SQLModel):
    """게시글 생성 요청 스키마"""

    title: str = Field(max_length=200)
    content: str


class PostUpdate(SQLModel):
    """게시글 수정 요청 스키마"""

    title: str | None = Field(default=None, max_length=200)
    content: str | None = None


class PostResponse(SQLModel):
    """게시글 응답 스키마"""

    id: int
    title: str
    content: str
    author_id: int
    author_nickname: str = ""
    created_at: datetime
    updated_at: datetime


class PostListResponse(SQLModel):
    """게시글 목록 응답 스키마 (페이지네이션 포함)"""

    items: list[PostResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
