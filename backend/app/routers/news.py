from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.company import Company
from app.services.data_transformer import get_clean_news
from app.models.scores import SentimentScore
from datetime import date, timedelta

router = APIRouter()


@router.get("/{ticker}")
def get_news(
    ticker: str,
    days:   int = Query(default=7, ge=1, le=30),
    db:     Session = Depends(get_db),
):
    # Return recent news articles with sentiment scores for a ticker
    ticker  = ticker.upper()
    company = db.query(Company).filter(Company.ticker == ticker).first()

    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{ticker}' not found")

    df = get_clean_news(db, ticker, days=days)

    if df.empty:
        return {"ticker": ticker, "articles": [], "sentiment_trend": []}

    articles = []
    for _, row in df.iterrows():
        articles.append({
            "title":              row["title"],
            "source":             row["source"],
            "published_at":       str(row["published_at"]),
            "sentiment_label":    row["sentiment_label"],
            "sentiment_compound": row["sentiment_compound"],
            "hype_keyword_count": int(row["hype_keyword_count"]),
        })

    # Also return the daily sentiment trend for charting
    cutoff = date.today() - timedelta(days=days)
    sentiment_rows = (
        db.query(SentimentScore)
        .filter(
            SentimentScore.ticker == ticker,
            SentimentScore.date   >= cutoff,
        )
        .order_by(SentimentScore.date.asc())
        .all()
    )

    sentiment_trend = [
        {
            "date":           str(s.date),
            "avg_compound":   s.avg_compound,
            "article_count":  s.article_count,
            "positive_count": s.positive_count,
            "negative_count": s.negative_count,
        }
        for s in sentiment_rows
    ]

    return {
        "ticker":          ticker,
        "articles":        articles,
        "sentiment_trend": sentiment_trend,
    }