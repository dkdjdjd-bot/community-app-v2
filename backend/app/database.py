"""SQLModel 데이터베이스 엔진 및 세션 설정"""

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

# SQLite 엔진 생성 (check_same_thread=False: FastAPI 멀티스레드 지원)
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)


def create_db_and_tables():
    """데이터베이스 테이블 생성"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """요청별 데이터베이스 세션 제공 (의존성 주입용)"""
    with Session(engine) as session:
        yield session
