import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
import numpy as np
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.price import Price
from app.models.news import NewsArticle
from app.models.financials import Financials


def get_clean_prices(db: Session, ticker: str, days: int = 90) -> pd.DataFrame:
    """
    Fetch and clean price data for a ticker.
    Returns a DataFrame sorted by date with no gaps or nulls in close price.
    """
    cutoff = date.today() - timedelta(days=days)

    rows = (
        db.query(Price)
        .filter(Price.ticker == ticker, Price.date >= cutoff)
        .order_by(Price.date.asc())
        .all()
    )

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame([{
        "date":   r.date,
        "open":   r.open,
        "high":   r.high,
        "low":    r.low,
        "close":  r.close,
        "volume": r.volume,
    } for r in rows])

    df = df.dropna(subset=["close"])

    for col in ["open", "high", "low"]:
        df[col] = df[col].fillna(df["close"])

    df["pct_change"]      = df["close"].pct_change()
    df["rolling_7d_avg"]  = df["close"].rolling(window=7).mean()
    df["rolling_30d_avg"] = df["close"].rolling(window=30).mean()

    # Price momentum: % change over last 30 days
    if len(df) >= 30:
        df["momentum_30d"] = (df["close"].iloc[-1] - df["close"].iloc[-30]) / df["close"].iloc[-30]
    else:
        df["momentum_30d"] = None

    return df.reset_index(drop=True)


def get_price_momentum(db: Session, ticker: str) -> dict:
    df = get_clean_prices(db, ticker, days=90)

    if df.empty:
        return {"momentum_30d": 0.0, "volatility_30d": 0.0, "current_price": 0.0}

    recent = df.tail(30)

    return {
        "current_price":  round(float(df["close"].iloc[-1]), 2),
        "momentum_30d":   round(float(df["momentum_30d"].iloc[-1] or 0), 4),
        "volatility_30d": round(float(recent["pct_change"].std() * np.sqrt(252)), 4),
        "avg_volume_30d": round(float(recent["volume"].mean() or 0), 0),
    }


# Words that suggest high hype / buzz
HYPE_KEYWORDS = [
    "surge", "soar", "skyrocket", "explode", "revolutionary", "game-changer",
    "disrupt", "breakout", "moon", "record", "milestone", "breakthrough",
    "massive", "incredible", "unstoppable", "dominat", "crushing", "beat",
    "rally", "bull", "boom", "frenzy", "mania", "hype"
]


def get_clean_news(db: Session, ticker: str, days: int = 7) -> pd.DataFrame:
    cutoff = date.today() - timedelta(days=days)

    rows = (
        db.query(NewsArticle)
        .filter(
            NewsArticle.ticker == ticker,
            NewsArticle.published_at >= cutoff
        )
        .order_by(NewsArticle.published_at.desc())
        .all()
    )

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame([{
        "id":                 r.id,
        "title":              r.title,
        "summary":            r.summary or "",
        "url":                r.url or "",
        "source":             r.source or "",
        "published_at":       r.published_at,
        "sentiment_compound": r.sentiment_compound,
        "sentiment_label":    r.sentiment_label,
    } for r in rows])

    # Remove articles with duplicate titles (same story, different URL)
    df = df.drop_duplicates(subset=["title"])

    # Count hype keywords in title (case-insensitive)
    def count_hype_keywords(title: str) -> int:
        title_lower = title.lower()
        return sum(1 for kw in HYPE_KEYWORDS if kw in title_lower)

    df["hype_keyword_count"] = df["title"].apply(count_hype_keywords)

    return df.reset_index(drop=True)


def get_news_buzz_metrics(db: Session, ticker: str, days: int = 7) -> dict:
    """
    Returns aggregated news buzz metrics for a ticker.
    Used as inputs to the Hype Score.
    """
    df = get_clean_news(db, ticker, days=days)

    if df.empty:
        return {
            "article_count":       0,
            "avg_sentiment":       0.0,
            "hype_keyword_total":  0,
            "positive_ratio":      0.0,
        }

    # Only include articles that have been sentiment-scored
    scored = df.dropna(subset=["sentiment_compound"])

    avg_sentiment = float(scored["sentiment_compound"].mean()) if not scored.empty else 0.0

    positive_count = len(df[df["sentiment_label"] == "positive"])
    positive_ratio = positive_count / len(df) if len(df) > 0 else 0.0

    return {
        "article_count":      len(df),
        "avg_sentiment":      round(avg_sentiment, 4),
        "hype_keyword_total": int(df["hype_keyword_count"].sum()),
        "positive_ratio":     round(positive_ratio, 4),
    }

# Reasonable bounds for financial ratios
# Values outside these ranges get clipped to avoid breaking the scoring
RATIO_BOUNDS = {
    "pe_ratio":            (0,   500),
    "pb_ratio":            (0,   100),
    "ps_ratio":            (0,   100),
    "net_margin":          (-1,  1),
    "gross_margin":        (0,   1),
    "operating_margin":    (-1,  1),
    "debt_to_equity":      (0,   500),
    "revenue_growth_yoy":  (-1,  5),
    "earnings_growth_yoy": (-5,  10),
}


def get_clean_financials(db: Session, ticker: str) -> dict:
    """
    Fetch the most recent financials row for a ticker and clean it.
    Clips outlier values to reasonable bounds.
    Returns a flat dict of metrics.
    """
    row = (
        db.query(Financials)
        .filter(Financials.ticker == ticker)
        .order_by(Financials.period_date.desc())
        .first()
    )

    if not row:
        return {}

    raw = {
        "pe_ratio":            row.pe_ratio,
        "pb_ratio":            row.pb_ratio,
        "ps_ratio":            row.ps_ratio,
        "net_margin":          row.net_margin,
        "gross_margin":        row.gross_margin,
        "operating_margin":    row.operating_margin,
        "debt_to_equity":      row.debt_to_equity,
        "revenue_growth_yoy":  row.revenue_growth_yoy,
        "earnings_growth_yoy": row.earnings_growth_yoy,
        "revenue":             row.revenue,
        "net_income":          row.net_income,
        "eps":                 row.eps,
    }

    cleaned = {}
    for key, value in raw.items():
        if value is None:
            cleaned[key] = None
            continue
        if key in RATIO_BOUNDS:
            lo, hi = RATIO_BOUNDS[key]
            cleaned[key] = max(lo, min(hi, float(value)))
        else:
            cleaned[key] = float(value)

    return cleaned