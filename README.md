# Finance Tracker API

개인 가계부 REST API — FastAPI + SQLite + JWT 인증

## 기능

- 회원가입 / 로그인 (JWT Bearer 토큰)
- 거래 내역 CRUD (수입/지출)
- 카테고리 · 날짜 · 타입 필터링
- 월별 수입/지출/잔액 통계

## 기술 스택

| 분류 | 기술 |
|------|------|
| 프레임워크 | FastAPI |
| DB ORM | SQLAlchemy 2.0 |
| 데이터베이스 | SQLite |
| 인증 | JWT (python-jose) |
| 암호화 | bcrypt |
| 유효성 검사 | Pydantic v2 |

## 실행 방법

```bash
# 패키지 설치
pip install -r requirements.txt

# 서버 실행
uvicorn app.main:app --reload

# 자동 생성 API 문서 확인
# http://localhost:8000/docs
```

## API 엔드포인트

### 인증
| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/auth/register` | 회원가입 |
| POST | `/auth/login` | 로그인 → JWT 발급 |
| GET | `/users/me` | 내 정보 조회 |

### 거래 내역 (인증 필요)
| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/transactions` | 거래 추가 |
| GET | `/transactions` | 목록 조회 (필터 지원) |
| GET | `/transactions/summary` | 월별 통계 |
| GET | `/transactions/{id}` | 단건 조회 |
| PATCH | `/transactions/{id}` | 수정 |
| DELETE | `/transactions/{id}` | 삭제 |

### 쿼리 파라미터 (목록 조회)
- `type` — `income` 또는 `expense`
- `category` — 카테고리 이름
- `start_date` / `end_date` — 날짜 범위 (`YYYY-MM-DD`)
- `skip` / `limit` — 페이징

## 사용 예시

```bash
# 회원가입
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"홍길동","password":"mypassword"}'

# 로그인
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"mypassword"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 수입 추가
curl -X POST http://localhost:8000/transactions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"월급","amount":3000000,"type":"income","category":"급여","transaction_date":"2026-06-01"}'

# 6월 통계 확인
curl "http://localhost:8000/transactions/summary?year=2026&month=6" \
  -H "Authorization: Bearer $TOKEN"
```

## 프로젝트 구조

```
finance-tracker/
├── app/
│   ├── main.py           # FastAPI 앱 진입점
│   ├── config.py         # 환경 설정
│   ├── database.py       # DB 연결 / 세션
│   ├── dependencies.py   # 인증 의존성
│   ├── models/           # SQLAlchemy 모델
│   │   ├── user.py
│   │   └── transaction.py
│   ├── schemas/          # Pydantic 스키마 (요청/응답)
│   │   ├── user.py
│   │   └── transaction.py
│   ├── services/         # 비즈니스 로직
│   │   ├── auth.py
│   │   └── transaction.py
│   └── routers/          # API 라우터
│       ├── auth.py
│       ├── users.py
│       └── transactions.py
└── requirements.txt
```
