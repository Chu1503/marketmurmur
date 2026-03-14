from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import companies, prices, news, scores

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Autonomous Market Intelligence Platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(companies.router, prefix="/api/v1/companies", tags=["companies"])
app.include_router(prices.router,    prefix="/api/v1/prices",    tags=["prices"])
app.include_router(news.router,      prefix="/api/v1/news",      tags=["news"])
app.include_router(scores.router,    prefix="/api/v1/scores",    tags=["scores"])

@app.get("/")
def root():
    return {"message": "MarketMurmur API", "version": settings.app_version}

@app.get("/health")
def health():
    return {"status": "ok"}