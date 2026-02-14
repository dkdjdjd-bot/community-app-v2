# Implementation Plan: 커뮤니티 게시판

**Branch**: `001-community-board` | **Date**: 2026-02-14 | **Spec**: `specs/001-community-board/spec.md`
**Input**: Feature specification from `/specs/001-community-board/spec.md`

## Summary

React + TypeScript + Vite + Tailwind 기반 Frontend와 FastAPI + SQLAlchemy + SQLite 기반 Backend로 구성된 커뮤니티 게시판 웹 애플리케이션. JWT 인증, 게시글 CRUD, 댓글 CRUD, 페이지네이션을 포함한 풀스택 구현.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript 5.x (Frontend)  
**Primary Dependencies**: FastAPI, SQLModel (SQLAlchemy + Pydantic v2 통합), python-jose (JWT), passlib[bcrypt] (Backend) / React 18, React Router v6, Axios, Tailwind CSS 3.x (Frontend)  
**Storage**: SQLite (SQLModel 사용, 개발/테스트 환경)  
**Testing**: pytest + httpx (Backend), vitest + React Testing Library (Frontend)  
**Target Platform**: Web (SPA + REST API)  
**Project Type**: Web application (frontend + backend)  
**Performance Goals**: 페이지 로드 2초 이내, API 응답 500ms 이내  
**Constraints**: SQLite 단일 파일 DB, JWT 만료 30분, 비밀번호 8자 이상  
**Scale/Scope**: 단일 개발자, MVP 수준, 소규모 커뮤니티 (수백 명 사용자)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 원칙 | 상태 | 비고 |
|------|------|------|
| 테스트 우선 (Test First) | ✅ PASS | TDD 방식 채택: pytest (backend), vitest (frontend). Red-Green-Refactor 사이클 준수 |
| 사용자 중심 (User-Centric) | ✅ PASS | 사용자 시나리오 기반 명세, 직관적 UI 설계 |
| 단순함 (Simplicity) | ✅ PASS | SQLite + 단순 JWT 인증, YAGNI 원칙 준수 (소셜 로그인 등 불필요 기능 배제) |
| 보안 (Security) | ✅ PASS | JWT 인증, bcrypt 해싱, 입력 검증, 권한 확인 |
| 품질 기준 | ✅ PASS | 핵심 로직 테스트 커버리지 80%+ 목표, API 응답 500ms 이내 |
| 개발 워크플로우 | ✅ PASS | Feature 브랜치 기반, spec-kit 명세 우선 개발 |

## Project Structure

### Documentation (this feature)

```text
specs/001-community-board/
├── spec.md              # 기능 명세서
├── plan.md              # 이 파일 (구현 계획)
└── tasks.md             # 태스크 목록
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱 진입점
│   ├── config.py            # 환경 설정 (DB URL, JWT Secret 등)
│   ├── database.py          # SQLModel 엔진/세션 설정
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User 모델
│   │   ├── post.py          # Post 모델
│   │   └── comment.py       # Comment 모델
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py          # User Pydantic 스키마
│   │   ├── post.py          # Post Pydantic 스키마
│   │   └── comment.py       # Comment Pydantic 스키마
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py          # 의존성 (get_db, get_current_user)
│   │   ├── auth.py          # 인증 라우터 (/auth/*)
│   │   ├── posts.py         # 게시글 라우터 (/posts/*)
│   │   └── comments.py      # 댓글 라우터 (/posts/{id}/comments/*)
│   └── services/
│       ├── __init__.py
│       ├── auth.py          # 인증 서비스 (JWT 생성/검증, 비밀번호 해싱)
│       ├── post.py          # 게시글 서비스 (CRUD 로직)
│       └── comment.py       # 댓글 서비스 (CRUD 로직)
├── tests/
│   ├── conftest.py          # 테스트 공통 픽스처 (TestClient, DB 세션)
│   ├── test_auth.py         # 인증 API 테스트
│   ├── test_posts.py        # 게시글 API 테스트
│   └── test_comments.py     # 댓글 API 테스트
├── requirements.txt
└── pyproject.toml

frontend/
├── src/
│   ├── main.tsx             # React 앱 진입점
│   ├── App.tsx              # 라우터 설정
│   ├── api/
│   │   └── client.ts        # Axios 인스턴스 + 인터셉터
│   ├── hooks/
│   │   ├── useAuth.ts       # 인증 관련 훅
│   │   ├── usePosts.ts      # 게시글 관련 훅
│   │   └── useComments.ts   # 댓글 관련 훅
│   ├── pages/
│   │   ├── LoginPage.tsx    # 로그인 페이지
│   │   ├── RegisterPage.tsx # 회원가입 페이지
│   │   ├── PostListPage.tsx # 게시글 목록 페이지
│   │   ├── PostDetailPage.tsx # 게시글 상세 페이지
│   │   └── PostFormPage.tsx # 게시글 작성/수정 페이지
│   ├── components/
│   │   ├── Layout.tsx       # 공통 레이아웃 (헤더, 네비게이션)
│   │   ├── PostCard.tsx     # 게시글 카드 컴포넌트
│   │   ├── CommentItem.tsx  # 댓글 아이템 컴포넌트
│   │   ├── CommentForm.tsx  # 댓글 입력 폼
│   │   ├── Pagination.tsx   # 페이지네이션 컴포넌트
│   │   └── ProtectedRoute.tsx # 인증 라우트 가드
│   ├── contexts/
│   │   └── AuthContext.tsx  # 인증 상태 관리 (Context API)
│   └── types/
│       └── index.ts         # 공통 타입 정의
├── tests/
│   ├── setup.ts             # vitest 설정
│   ├── pages/
│   │   ├── LoginPage.test.tsx
│   │   ├── PostListPage.test.tsx
│   │   └── PostDetailPage.test.tsx
│   └── components/
│       ├── PostCard.test.tsx
│       └── Pagination.test.tsx
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

**Structure Decision**: Web application 구조 (frontend + backend 분리). Backend는 FastAPI 기반 REST API 서버, Frontend는 React SPA. CORS 설정으로 개발 환경에서 cross-origin 요청 허용.

## 구현 순서

### Phase 1: Backend 기반 설정
1. 프로젝트 구조 생성 및 의존성 설치
2. SQLAlchemy DB 설정 (SQLite)
3. User, Post, Comment 모델 정의
4. 테스트 인프라 구축 (conftest.py, TestClient)

### Phase 2: 인증 API (JWT)
1. 인증 서비스 구현 (비밀번호 해싱, JWT 생성/검증)
2. Pydantic 스키마 정의 (UserCreate, UserLogin, Token)
3. 인증 라우터 구현 (POST /auth/register, POST /auth/login)
4. 인증 미들웨어/의존성 (get_current_user)

### Phase 3: 게시글 API
1. 게시글 Pydantic 스키마 (PostCreate, PostUpdate, PostResponse)
2. 게시글 서비스 (CRUD 로직, 권한 확인)
3. 게시글 라우터 (GET/POST/PUT/DELETE /posts/*)
4. 페이지네이션 구현

### Phase 4: 댓글 API
1. 댓글 Pydantic 스키마 (CommentCreate, CommentUpdate, CommentResponse)
2. 댓글 서비스 (CRUD 로직, 권한 확인)
3. 댓글 라우터 (GET/POST/PUT/DELETE /posts/{id}/comments/*)

### Phase 5: Frontend 기본 구조
1. Vite + React + TypeScript 프로젝트 초기화
2. Tailwind CSS 설정
3. Axios 클라이언트 + JWT 인터셉터
4. AuthContext + 라우팅 설정
5. 공통 레이아웃 컴포넌트

### Phase 6: Frontend 페이지별 UI
1. 회원가입/로그인 페이지
2. 게시글 목록 페이지 (페이지네이션 포함)
3. 게시글 상세 페이지 (댓글 포함)
4. 게시글 작성/수정 페이지
5. ProtectedRoute 구현

### Phase 7: 통합 및 마무리
1. Frontend ↔ Backend 통합 테스트
2. CORS 설정 확인
3. 에러 핸들링 통합
4. 코드 정리 및 문서화

## 테스트 전략

### Backend (pytest)
- **단위 테스트**: 서비스 레이어 함수별 테스트 (비밀번호 해싱, JWT 생성/검증, CRUD 로직)
- **통합 테스트**: API 엔드포인트별 테스트 (httpx AsyncClient 사용)
- **TDD 방식**: 테스트 작성 → 실패 확인 → 구현 → 통과 확인 → 리팩토링

### Frontend (vitest)
- **컴포넌트 테스트**: React Testing Library로 렌더링/상호작용 테스트
- **훅 테스트**: renderHook으로 커스텀 훅 테스트
- **TDD 방식**: 컴포넌트 스펙 → 테스트 작성 → 구현

### 커버리지 목표
- 핵심 비즈니스 로직 (서비스 레이어): 80% 이상
- API 엔드포인트: 주요 시나리오 100%
- Frontend 컴포넌트: 주요 인터랙션 커버

## Complexity Tracking

> Constitution Check에 위반 사항 없음. 별도 정당화 불필요.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (해당 없음) | — | — |
