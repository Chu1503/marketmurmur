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
from app.services.company_lookup import get_or_create_company
import json
import math

def sanitize_json(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_json(i) for i in obj]
    return obj

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
    company = get_or_create_company(db, ticker)

    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Company '{ticker}' not found or invalid ticker"
        )

    latest_score = (
        db.query(HypeScore)
        .filter(HypeScore.ticker == ticker)
        .order_by(HypeScore.calculated_at.desc())
        .first()
    )

    if not latest_score:
        try:
            from app.services.sentiment import run_sentiment_analysis
            from app.services.hype_score import compute_and_save_hype_score
            run_sentiment_analysis(db, ticker)
            compute_and_save_hype_score(db, ticker)
            latest_score = (
                db.query(HypeScore)
                .filter(HypeScore.ticker == ticker)
                .order_by(HypeScore.calculated_at.desc())
                .first()
            )
        except Exception as e:
            print(f"  Could not compute score for {ticker}: {e}")

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

    response = {
        "company":     {
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
    return sanitize_json(response)

@app.post("/api/v1/run/stocks")
def trigger_stock_collector(db: Session = Depends(get_db)):
    # Called by n8n every 6 hours to refresh stock prices
    import sys
    sys.path.insert(0, ".")
    from collectors.stock_collector import run
    try:
        run()
        return {"status": "ok", "job": "stock_collector"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/run/news")
def trigger_news_collector(db: Session = Depends(get_db)):
    # Called by n8n every 4 hours to fetch new articles
    from collectors.news_collector import run
    try:
        run()
        return {"status": "ok", "job": "news_collector"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/run/analytics")
def trigger_analytics(db: Session = Depends(get_db)):
    # Called by n8n daily to run sentiment analysis and hype scores
    from app.services.sentiment import run_full_sentiment_pipeline
    from app.services.hype_score import run_all_hype_scores
    try:
        run_full_sentiment_pipeline(db)
        run_all_hype_scores(db)
        return {"status": "ok", "job": "analytics"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/run/financials")
def trigger_financials_collector(db: Session = Depends(get_db)):
    # Called by n8n daily to refresh financial metrics
    from collectors.financials_collector import run
    try:
        run()
        return {"status": "ok", "job": "financials_collector"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))