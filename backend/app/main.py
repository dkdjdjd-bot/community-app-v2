"""FastAPI 애플리케이션 진입점"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.config import settings
from app.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작 시 DB 테이블 생성"""
    create_db_and_tables()
    yield


app = FastAPI(
    title="커뮤니티 게시판 API",
    description="커뮤니티 게시판 REST API 서버",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 라우터 등록
app.include_router(auth_router)


@app.get("/health")
def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "ok"}
