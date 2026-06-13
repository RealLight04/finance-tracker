from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import auth, transactions, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="개인 가계부 REST API - 수입/지출 관리 및 월별 통계 제공",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(transactions.router)


@app.get("/", tags=["상태 확인"])
def root():
    return {"status": "ok", "app": settings.app_name}
