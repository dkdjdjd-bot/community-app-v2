"""인증 라우터 — 회원가입, 로그인, 사용자 정보 조회"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.database import get_session
from app.models.user import Token, User, UserCreate, UserLogin, UserResponse
from app.services.auth import (
    create_access_token,
    create_user,
    get_user_by_email,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["인증"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    """회원가입 — 이메일/비밀번호/닉네임으로 새 계정 생성"""
    # 중복 이메일 확인
    existing = get_user_by_email(session, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 등록된 이메일입니다",
        )

    user = create_user(session, user_data)
    return user


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, session: Session = Depends(get_session)):
    """로그인 — 이메일/비밀번호 검증 후 JWT 토큰 발급"""
    user = get_user_by_email(session, login_data.email)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """현재 로그인된 사용자 정보 조회"""
    return current_user
