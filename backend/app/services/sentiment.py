import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date, timedelta
from app.models.news import NewsArticle
from app.models.scores import SentimentScore
from app.models.company import Company

analyzer = SentimentIntensityAnalyzer()


def score_text(text: str) -> dict:
    """
    Run VADER sentiment analysis on a piece of text.
    Returns compound (-1 to 1), positive, negative, neutral scores
    and a human-readable label.

    VADER is specifically tuned for short social/news text.
    compound > 0.05  = positive
    compound < -0.05 = negative
    otherwise        = neutral
    """
    if not text or not text.strip():
        return {
            "compound":  0.0,
            "positive":  0.0,
            "negative":  0.0,
            "neutral":   1.0,
            "label":     "neutral",
        }

    scores = analyzer.polarity_scores(text)

    if scores["compound"] >= 0.05:
        label = "positive"
    elif scores["compound"] <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return {
        "compound": round(scores["compound"], 4),
        "positive": round(scores["pos"],      4),
        "negative": round(scores["neg"],      4),
        "neutral":  round(scores["neu"],      4),
        "label":    label,
    }


def score_article(article: NewsArticle) -> dict:
    text = article.title or ""
    if article.summary:
        text = text + ". " + article.summary[:500]

    return score_text(text)


def run_sentiment_analysis(db: Session, ticker: str = None) -> dict:
    query = db.query(NewsArticle).filter(
        NewsArticle.sentiment_compound == None  # only unscored articles
    )

    if ticker:
        query = query.filter(NewsArticle.ticker == ticker)

    articles = query.all()

    if not articles:
        print("  No unscored articles found.")
        return {"scored": 0}

    print(f"  Scoring {len(articles)} articles...")
    scored_count = 0

    for article in articles:
        result = score_article(article)

        article.sentiment_compound = result["compound"]
        article.sentiment_positive = result["positive"]
        article.sentiment_negative = result["negative"]
        article.sentiment_neutral  = result["neutral"]
        article.sentiment_label    = result["label"]
        scored_count += 1

    db.commit()
    print(f"  Scored {scored_count} articles.")
    return {"scored": scored_count}


def aggregate_daily_sentiment(db: Session, ticker: str) -> dict:
    # Get all scored articles for this ticker from the last 30 days
    cutoff = date.today() - timedelta(days=30)

    articles = (
        db.query(NewsArticle)
        .filter(
            NewsArticle.ticker == ticker,
            NewsArticle.sentiment_compound != None,
            NewsArticle.published_at >= cutoff,
        )
        .all()
    )

    if not articles:
        return {"days_aggregated": 0}

    by_date = {}
    for article in articles:
        if not article.published_at:
            continue
        day = article.published_at.date()
        if day not in by_date:
            by_date[day] = []
        by_date[day].append(article)

    days_aggregated = 0

    for day, day_articles in by_date.items():
        compounds = [a.sentiment_compound for a in day_articles if a.sentiment_compound is not None]

        if not compounds:
            continue

        positive_count = sum(1 for a in day_articles if a.sentiment_label == "positive")
        negative_count = sum(1 for a in day_articles if a.sentiment_label == "negative")
        neutral_count  = sum(1 for a in day_articles if a.sentiment_label == "neutral")

        existing = (
            db.query(SentimentScore)
            .filter(SentimentScore.ticker == ticker, SentimentScore.date == day)
            .first()
        )

        if existing:
            existing.article_count  = len(day_articles)
            existing.avg_compound   = sum(compounds) / len(compounds)
            existing.positive_count = positive_count
            existing.negative_count = negative_count
            existing.neutral_count  = neutral_count
        else:
            score = SentimentScore(
                ticker         = ticker,
                date           = day,
                article_count  = len(day_articles),
                avg_compound   = sum(compounds) / len(compounds),
                positive_count = positive_count,
                negative_count = negative_count,
                neutral_count  = neutral_count,
            )
            db.add(score)

        days_aggregated += 1

    db.commit()
    return {"days_aggregated": days_aggregated}


def run_full_sentiment_pipeline(db: Session) -> None:
    """
    Convenience function that runs the complete sentiment pipeline:
    1. Score all unscored articles across all tickers
    2. Aggregate into daily sentiment scores for each ticker
    """
    print("Running sentiment pipeline...")

    run_sentiment_analysis(db)

    companies = db.query(Company).all()
    for company in companies:
        result = aggregate_daily_sentiment(db, company.ticker)
        print(f"  {company.ticker}: {result['days_aggregated']} days aggregated")

    print("Sentiment pipeline complete.")