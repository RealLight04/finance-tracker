from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import auth, products, transactions, users
from app.seed_products import seed_products

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    seed_products(db)

app = FastAPI(
    title=settings.app_name,
    description="PX 가계부 API - 상품 검색, 수입/지출 관리 및 월별 통계 제공",
    version="1.1.0",
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
app.include_router(products.router)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", tags=["상태 확인"])
def health():
    return {"status": "ok", "app": settings.app_name}
