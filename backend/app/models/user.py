"""User 모델 — 사용자 테이블 및 스키마"""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """사용자 기본 필드"""

    email: str = Field(unique=True, index=True, max_length=255)
    nickname: str = Field(max_length=50)


class User(UserBase, table=True):
    """사용자 DB 테이블 모델"""

    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserCreate(SQLModel):
    """회원가입 요청 스키마"""

    email: str = Field(max_length=255)
    password: str = Field(min_length=8)
    nickname: str = Field(max_length=50)


class UserLogin(SQLModel):
    """로그인 요청 스키마"""

    email: str
    password: str


class UserResponse(SQLModel):
    """사용자 응답 스키마 (비밀번호 제외)"""

    id: int
    email: str
    nickname: str
    created_at: datetime


class Token(SQLModel):
    """JWT 토큰 응답 스키마"""

    access_token: str
    token_type: str = "bearer"
