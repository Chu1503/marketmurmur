from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.routers import companies, prices, news, scores
from app.models.company import Company
from app.models.scores import HypeScore
from app.services.data_transformer import get_clean_prices, get_clean_news, get_price_momentum
from app.services.competitor import get_competitor_comparison
import json

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.railway.app",
                   "https://*.vercel.app"],
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
    return {
        "message": "MarketMurmur API",
        "version": settings.app_version,
        "docs":    "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/dashboard/{ticker}")
def get_dashboard(ticker: str, db: Session = Depends(get_db)):
    """
    Single endpoint that returns everything the dashboard needs.
    Combines company info, prices, news, scores, and competitors
    into one response so the frontend makes one HTTP request.
    """
    ticker  = ticker.upper()
    company = db.query(Company).filter(Company.ticker == ticker).first()

    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{ticker}' not found")

    latest_score = (
        db.query(HypeScore)
        .filter(HypeScore.ticker == ticker)
        .order_by(HypeScore.calculated_at.desc())
        .first()
    )

    score_data = None
    if latest_score:
        breakdown = {}
        if latest_score.inputs_json:
            try:
                breakdown = json.loads(latest_score.inputs_json)
            except Exception:
                pass
        score_data = {
            "hype_score":  latest_score.hype_score,
            "fund_score":  latest_score.fund_score,
            "hype_gap":    latest_score.hype_gap,
            "label":       latest_score.label,
            "breakdown":   breakdown,
            "calculated_at": str(latest_score.calculated_at),
        }

    # Recent prices (90 days)
    price_df  = get_clean_prices(db, ticker, days=90)
    momentum  = get_price_momentum(db, ticker)

    prices = []
    if not price_df.empty:
        for _, row in price_df.iterrows():
            prices.append({
                "date":  str(row["date"]),
                "close": round(float(row["close"]), 2),
                "volume": int(row["volume"]) if row["volume"] else None,
                "rolling_7d_avg": round(float(row["rolling_7d_avg"]), 2)
                                  if row["rolling_7d_avg"] and
                                     str(row["rolling_7d_avg"]) != "nan"
                                  else None,
            })

    # Recent news (7 days)
    news_df = get_clean_news(db, ticker, days=7)
    articles = []
    if not news_df.empty:
        for _, row in news_df.head(10).iterrows():
            articles.append({
                "title":           row["title"],
                "source":          row["source"],
                "published_at":    str(row["published_at"]),
                "sentiment_label": row["sentiment_label"],
                "sentiment_compound": row["sentiment_compound"],
            })

    # Competitor Comparison
    comparison = get_competitor_comparison(db, ticker)

    return {
        "company":    {
            "ticker":      company.ticker,
            "name":        company.name,
            "sector":      company.sector,
            "industry":    company.industry,
            "description": company.description,
            "employees":   company.employees,
            "website":     company.website,
            "market_cap":  company.market_cap,
        },
        "score":      score_data,
        "momentum":   momentum,
        "prices":     prices,
        "news":       articles,
        "competitors": comparison["comparisons"],
    }