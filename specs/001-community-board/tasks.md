# Tasks: 커뮤니티 게시판

**Input**: Design documents from `/specs/001-community-board/`
**Prerequisites**: plan.md (required), spec.md (required)

**Tests**: TDD 방식 — 모든 기능에 대해 테스트를 먼저 작성하고 실패를 확인한 후 구현합니다.

**Organization**: User Story 기반으로 그룹화하여 독립적 구현/테스트가 가능하도록 구성.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 실행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 해당 태스크가 속한 User Story (US1, US2, US3, US4)
- 파일 경로 포함

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (프로젝트 초기화)

**Purpose**: 프로젝트 구조 생성 및 개발 환경 설정

**예상 소요 시간**: 1시간

- [ ] T001 Backend 프로젝트 디렉토리 구조 생성 및 pyproject.toml / requirements.txt 작성 (`backend/`)
- [ ] T002 [P] FastAPI 앱 진입점 생성 (`backend/app/main.py`, `backend/app/__init__.py`)
- [ ] T003 [P] 환경 설정 모듈 생성 — DB URL, JWT Secret, 토큰 만료 시간 (`backend/app/config.py`)
- [ ] T004 SQLAlchemy 엔진/세션 설정 — SQLite 연결, Base 선언 (`backend/app/database.py`)
- [ ] T005 테스트 인프라 구축 — TestClient, 테스트용 DB 세션 픽스처 (`backend/tests/conftest.py`)
- [ ] T006 [P] Frontend 프로젝트 초기화 — Vite + React + TypeScript (`frontend/`)
- [ ] T007 [P] Tailwind CSS 설정 (`frontend/tailwind.config.js`, `frontend/src/index.css`)
- [ ] T008 [P] vitest 설정 (`frontend/vite.config.ts`, `frontend/tests/setup.ts`)

**Checkpoint**: Backend/Frontend 프로젝트가 빌드 및 테스트 실행 가능 상태

---

## Phase 2: Foundational (핵심 인프라)

**Purpose**: 모든 User Story에 필요한 기반 코드 — 이 단계가 완료되어야 User Story 작업 가능

**예상 소요 시간**: 1.5시간

**⚠️ CRITICAL**: User Story 작업 시작 전 반드시 완료

- [ ] T009 User 모델 정의 — id, email, hashed_password, nickname, created_at (`backend/app/models/user.py`)
- [ ] T010 [P] Post 모델 정의 — id, title, content, author_id(FK), created_at, updated_at, is_deleted (`backend/app/models/post.py`)
- [ ] T011 [P] Comment 모델 정의 — id, content, author_id(FK), post_id(FK), created_at, updated_at (`backend/app/models/comment.py`)
- [ ] T012 모델 패키지 초기화 — Base.metadata에 모든 모델 등록 (`backend/app/models/__init__.py`)
- [ ] T013 [P] 공통 타입 정의 — User, Post, Comment, AuthToken 타입 (`frontend/src/types/index.ts`)
- [ ] T014 [P] Axios 클라이언트 인스턴스 생성 — base URL, JWT 인터셉터 (`frontend/src/api/client.ts`)

**Checkpoint**: DB 모델 정의 완료, Frontend 네트워크 레이어 준비

---

## Phase 3: User Story 1 — 회원가입 및 로그인 (Priority: P1) 🎯 MVP

**Goal**: 이메일/비밀번호로 회원가입, 로그인하여 JWT 토큰 발급. 인증 미들웨어로 보호된 API 접근 제어.

**Independent Test**: 회원가입 → 로그인 → JWT 발급 → 인증 API 접근 전체 흐름 검증

**예상 소요 시간**: 3시간

### 테스트 작성 (US1) ⚠️ 테스트 먼저!

> **NOTE: 테스트를 먼저 작성하고, 실패를 확인한 후 구현합니다**

- [ ] T015 [US1] 인증 API 테스트 작성 — 회원가입 성공/실패, 로그인 성공/실패, 중복 이메일, 잘못된 비밀번호 (`backend/tests/test_auth.py`)

### 구현 (US1)

- [ ] T016 [US1] User Pydantic 스키마 — UserCreate, UserLogin, UserResponse, Token (`backend/app/schemas/user.py`)
- [ ] T017 [US1] 인증 서비스 — 비밀번호 해싱(bcrypt), JWT 생성/검증, 사용자 생성/조회 (`backend/app/services/auth.py`)
- [ ] T018 [US1] 인증 의존성 — get_db, get_current_user (JWT 디코딩) (`backend/app/api/deps.py`)
- [ ] T019 [US1] 인증 라우터 — POST /auth/register, POST /auth/login (`backend/app/api/auth.py`)
- [ ] T020 [US1] FastAPI 앱에 인증 라우터 등록 및 CORS 설정 (`backend/app/main.py`)

**Checkpoint**: 회원가입/로그인 API 동작, 모든 인증 테스트 통과

---

## Phase 4: User Story 2 — 게시글 CRUD (Priority: P1) 🎯 MVP

**Goal**: 인증 사용자의 게시글 작성/수정/삭제, 전체 사용자의 게시글 목록/상세 조회, 페이지네이션

**Independent Test**: 게시글 작성 → 목록 조회 → 상세 조회 → 수정 → 삭제 전체 흐름, 권한 확인

**예상 소요 시간**: 3시간

### 테스트 작성 (US2) ⚠️ 테스트 먼저!

- [ ] T021 [US2] 게시글 API 테스트 작성 — CRUD 성공/실패, 페이지네이션, 권한 검증, 소프트 삭제 (`backend/tests/test_posts.py`)

### 구현 (US2)

- [ ] T022 [US2] 게시글 Pydantic 스키마 — PostCreate, PostUpdate, PostResponse, PostListResponse (`backend/app/schemas/post.py`)
- [ ] T023 [US2] 게시글 서비스 — 생성, 조회, 목록(페이지네이션), 수정, 삭제(소프트), 권한 확인 (`backend/app/services/post.py`)
- [ ] T024 [US2] 게시글 라우터 — GET /posts, GET /posts/{id}, POST /posts, PUT /posts/{id}, DELETE /posts/{id} (`backend/app/api/posts.py`)
- [ ] T025 [US2] FastAPI 앱에 게시글 라우터 등록 (`backend/app/main.py`)

**Checkpoint**: 게시글 CRUD API 동작, 모든 게시글 테스트 통과

---

## Phase 5: User Story 3 — 댓글 CRUD (Priority: P2)

**Goal**: 인증 사용자의 댓글 작성/수정/삭제, 게시글별 댓글 목록 조회

**Independent Test**: 댓글 작성 → 목록 조회 → 수정 → 삭제 전체 흐름, 권한 확인

**예상 소요 시간**: 2.5시간

### 테스트 작성 (US3) ⚠️ 테스트 먼저!

- [ ] T026 [US3] 댓글 API 테스트 작성 — CRUD 성공/실패, 권한 검증, 존재하지 않는 게시글 (`backend/tests/test_comments.py`)

### 구현 (US3)

- [ ] T027 [US3] 댓글 Pydantic 스키마 — CommentCreate, CommentUpdate, CommentResponse (`backend/app/schemas/comment.py`)
- [ ] T028 [US3] 댓글 서비스 — 생성, 조회, 수정, 삭제, 권한 확인 (`backend/app/services/comment.py`)
- [ ] T029 [US3] 댓글 라우터 — GET/POST /posts/{id}/comments, PUT/DELETE /posts/{id}/comments/{comment_id} (`backend/app/api/comments.py`)
- [ ] T030 [US3] FastAPI 앱에 댓글 라우터 등록 (`backend/app/main.py`)

**Checkpoint**: 댓글 CRUD API 동작, 모든 댓글 테스트 통과. Backend API 전체 완성.

---

## Phase 6: User Story 4 — Frontend UI (Priority: P2)

**Goal**: 웹 브라우저에서 전체 사용자 흐름을 수행할 수 있는 UI 구현

**Independent Test**: 브라우저에서 회원가입 → 로그인 → 게시글 작성 → 댓글 작성 전체 흐름 수행

**예상 소요 시간**: 5시간

### 테스트 작성 (US4) ⚠️ 테스트 먼저!

- [ ] T031 [P] [US4] 로그인 페이지 컴포넌트 테스트 — 렌더링, 폼 제출, 에러 표시 (`frontend/tests/pages/LoginPage.test.tsx`)
- [ ] T032 [P] [US4] 게시글 목록 페이지 컴포넌트 테스트 — 렌더링, 페이지네이션, 게시글 클릭 (`frontend/tests/pages/PostListPage.test.tsx`)
- [ ] T033 [P] [US4] 게시글 상세 페이지 컴포넌트 테스트 — 렌더링, 댓글 표시, 수정/삭제 버튼 (`frontend/tests/pages/PostDetailPage.test.tsx`)
- [ ] T034 [P] [US4] PostCard 컴포넌트 테스트 — 렌더링, 클릭 이벤트 (`frontend/tests/components/PostCard.test.tsx`)
- [ ] T035 [P] [US4] Pagination 컴포넌트 테스트 — 페이지 변경, 비활성화 상태 (`frontend/tests/components/Pagination.test.tsx`)

### 구현 (US4)

- [ ] T036 [US4] AuthContext — 로그인 상태 관리, 토큰 저장/삭제, 자동 로그아웃 (`frontend/src/contexts/AuthContext.tsx`)
- [ ] T037 [US4] useAuth 훅 — 로그인, 회원가입, 로그아웃 API 호출 (`frontend/src/hooks/useAuth.ts`)
- [ ] T038 [P] [US4] usePosts 훅 — 게시글 CRUD API 호출 (`frontend/src/hooks/usePosts.ts`)
- [ ] T039 [P] [US4] useComments 훅 — 댓글 CRUD API 호출 (`frontend/src/hooks/useComments.ts`)
- [ ] T040 [US4] Layout 컴포넌트 — 헤더, 네비게이션, 로그인/로그아웃 버튼 (`frontend/src/components/Layout.tsx`)
- [ ] T041 [US4] ProtectedRoute 컴포넌트 — 미인증 시 로그인 페이지 리다이렉트 (`frontend/src/components/ProtectedRoute.tsx`)
- [ ] T042 [P] [US4] 회원가입 페이지 — 이메일/비밀번호/닉네임 폼 (`frontend/src/pages/RegisterPage.tsx`)
- [ ] T043 [P] [US4] 로그인 페이지 — 이메일/비밀번호 폼 (`frontend/src/pages/LoginPage.tsx`)
- [ ] T044 [US4] PostCard 컴포넌트 — 게시글 요약 카드 (`frontend/src/components/PostCard.tsx`)
- [ ] T045 [US4] Pagination 컴포넌트 — 페이지 번호 네비게이션 (`frontend/src/components/Pagination.tsx`)
- [ ] T046 [US4] 게시글 목록 페이지 — PostCard + Pagination 조합 (`frontend/src/pages/PostListPage.tsx`)
- [ ] T047 [US4] CommentItem 컴포넌트 — 댓글 표시, 수정/삭제 버튼 (`frontend/src/components/CommentItem.tsx`)
- [ ] T048 [US4] CommentForm 컴포넌트 — 댓글 입력 폼 (`frontend/src/components/CommentForm.tsx`)
- [ ] T049 [US4] 게시글 상세 페이지 — 게시글 내용 + 댓글 목록/입력 (`frontend/src/pages/PostDetailPage.tsx`)
- [ ] T050 [US4] 게시글 작성/수정 페이지 — 제목/내용 폼, 수정 시 기존 데이터 로드 (`frontend/src/pages/PostFormPage.tsx`)
- [ ] T051 [US4] App 라우터 설정 — React Router v6, 모든 페이지 연결 (`frontend/src/App.tsx`)

**Checkpoint**: Frontend 전체 UI 동작, 컴포넌트 테스트 통과

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 통합 테스트, 코드 정리, 문서화

**예상 소요 시간**: 2시간

- [ ] T052 Frontend ↔ Backend 통합 확인 — CORS 설정, API 연동 테스트
- [ ] T053 [P] 에러 핸들링 통합 — 글로벌 에러 핸들러, 사용자 친화적 메시지 (`backend/app/main.py`, `frontend/src/api/client.ts`)
- [ ] T054 [P] README.md 작성 — 프로젝트 설명, 설치/실행 방법, API 문서 링크 (`README.md`)
- [ ] T055 코드 정리 및 린팅 — 불필요한 import 제거, 코드 스타일 통일
- [ ] T056 최종 테스트 실행 — Backend pytest 전체, Frontend vitest 전체 통과 확인

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 의존성 없음 — 즉시 시작 가능
- **Foundational (Phase 2)**: Setup 완료 필요 — 모든 User Story를 차단
- **US1 회원가입/로그인 (Phase 3)**: Foundational 완료 필요
- **US2 게시글 CRUD (Phase 4)**: US1 완료 필요 (인증 의존)
- **US3 댓글 CRUD (Phase 5)**: US2 완료 필요 (게시글 의존)
- **US4 Frontend UI (Phase 6)**: US1~US3 완료 권장 (Backend API 필요)
- **Polish (Phase 7)**: 모든 User Story 완료 필요

### User Story Dependencies

- **US1 (P1)**: Foundational 완료 후 시작 — 다른 Story 의존 없음
- **US2 (P1)**: US1 완료 필요 — 인증된 사용자만 게시글 작성 가능
- **US3 (P2)**: US2 완료 필요 — 게시글이 있어야 댓글 가능
- **US4 (P2)**: Backend API 전체(US1~US3) 완료 후 시작 권장

### Within Each User Story

- 테스트 먼저 작성 → 실패 확인 → 구현 → 테스트 통과 (TDD)
- 스키마 → 서비스 → 라우터 순서
- 핵심 기능 → 부가 기능 순서

### Parallel Opportunities

- Phase 1: T002/T003 병렬, T006/T007/T008 병렬 (Backend/Frontend 독립)
- Phase 2: T010/T011 병렬 (Post/Comment 모델), T013/T014 병렬 (Frontend)
- Phase 6: 테스트 T031~T035 모두 병렬, 컴포넌트 T042/T043 병렬, T038/T039 병렬

---

## Parallel Example: Phase 6 (Frontend UI)

```bash
# 테스트를 먼저 병렬 작성:
Task: "로그인 페이지 테스트 - frontend/tests/pages/LoginPage.test.tsx"
Task: "게시글 목록 페이지 테스트 - frontend/tests/pages/PostListPage.test.tsx"
Task: "PostCard 컴포넌트 테스트 - frontend/tests/components/PostCard.test.tsx"
Task: "Pagination 컴포넌트 테스트 - frontend/tests/components/Pagination.test.tsx"

# 구현 병렬 실행:
Task: "회원가입 페이지 - frontend/src/pages/RegisterPage.tsx"
Task: "로그인 페이지 - frontend/src/pages/LoginPage.tsx"
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Phase 1: Setup 완료
2. Phase 2: Foundational 완료
3. Phase 3: US1 회원가입/로그인 완료 → 테스트 검증
4. Phase 4: US2 게시글 CRUD 완료 → 테스트 검증
5. **STOP and VALIDATE**: Backend MVP 동작 확인
6. 필요시 배포/데모 가능

### Incremental Delivery

1. Setup + Foundational → 기반 준비
2. US1 → 인증 시스템 동작 (Backend MVP 1)
3. US2 → 게시글 기능 동작 (Backend MVP 2)
4. US3 → 댓글 기능 추가 (Backend 완성)
5. US4 → Frontend UI 추가 (풀스택 완성)
6. Polish → 최종 완성

### 총 예상 소요 시간

| Phase | 시간 |
|-------|------|
| Phase 1: Setup | 1시간 |
| Phase 2: Foundational | 1.5시간 |
| Phase 3: US1 인증 | 3시간 |
| Phase 4: US2 게시글 | 3시간 |
| Phase 5: US3 댓글 | 2.5시간 |
| Phase 6: US4 Frontend | 5시간 |
| Phase 7: Polish | 2시간 |
| **합계** | **18시간** |

---

## Notes

- [P] 태스크 = 다른 파일, 의존성 없음 → 병렬 가능
- [Story] 라벨 = 해당 태스크의 User Story 소속
- TDD 원칙 엄수: 테스트 작성 → 실패 확인 → 구현 → 통과
- 각 태스크 완료 후 커밋
- Checkpoint에서 독립 검증 수행
- 금지: 모호한 태스크, 같은 파일 충돌, Story 간 불필요한 의존성
