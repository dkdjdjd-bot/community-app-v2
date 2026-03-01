"""애플리케이션 설정 모듈"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """환경 설정 클래스"""

    # 데이터베이스 설정
    DATABASE_URL: str = "sqlite:///./community.db"

    # JWT 설정
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS 설정
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env"}


# 싱글턴 설정 인스턴스
settings = Settings()
