"""인증 서비스 — 비밀번호 해싱, JWT 생성/검증, 사용자 관리"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from app.config import settings
from app.models.user import User, UserCreate

# 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """비밀번호를 bcrypt로 해싱"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해시된 비밀번호 비교"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """JWT 토큰 디코딩 (실패 시 None 반환)"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def get_user_by_email(session: Session, email: str) -> User | None:
    """이메일로 사용자 조회"""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def create_user(session: Session, user_data: UserCreate) -> User:
    """새 사용자 생성"""
    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        nickname=user_data.nickname,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
