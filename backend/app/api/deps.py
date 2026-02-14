"""API 의존성 — DB 세션, 현재 사용자 인증"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.database import get_session
from app.models.user import User
from app.services.auth import decode_access_token

# Bearer 토큰 스키마 (auto_error=False: 토큰 없으면 None 반환)
security = HTTPBearer(auto_error=False)


def get_current_user(
    session: Session = Depends(get_session),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> User:
    """JWT 토큰에서 현재 사용자 추출 (인증 실패 시 401)"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 필요합니다",
        )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
        )

    user_id: int | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에 사용자 정보가 없습니다",
        )

    user = session.get(User, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다",
        )

    return user
