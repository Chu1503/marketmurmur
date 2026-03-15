import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models.company import Company
from app.models.news import NewsArticle
from app.config import get_settings

settings = get_settings()


def fetch_news_for_ticker(company_name: str, ticker: str, days_back: int = 7) -> list:
    """
    Fetch recent news articles from NewsAPI.
    Searches by company name for better results than ticker alone.
    Returns a list of article dicts.
    """
    if not settings.news_api_key or settings.news_api_key == "your_key_here":
        print(f"  WARNING: NEWS_API_KEY not set. Skipping news for {ticker}")
        return []

    end_date   = datetime.today()
    start_date = end_date - timedelta(days=days_back)

    url = "https://newsapi.org/v2/everything"
    params = {
        "q":          f'"{company_name}" OR "{ticker}"',
        "from":       start_date.strftime("%Y-%m-%d"),
        "to":         end_date.strftime("%Y-%m-%d"),
        "language":   "en",
        "sortBy":     "publishedAt",
        "pageSize":   30,   # max 30 articles per company per run
        "apiKey":     settings.news_api_key,
    }

    print(f"  Fetching news for {company_name} ({ticker})...")

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        articles = data.get("articles", [])
        print(f"  Got {len(articles)} articles for {ticker}")
        return articles

    except requests.exceptions.RequestException as e:
        print(f"  ERROR fetching news for {ticker}: {e}")
        return []


def save_articles(db, ticker: str, articles: list) -> dict:
    """
    Save news articles to the database.
    """
    inserted = 0
    skipped  = 0

    for article in articles:
        # Skip articles with no URL or title
        if not article.get("url") or not article.get("title"):
            continue

        published_at = None
        if article.get("publishedAt"):
            try:
                published_at = datetime.strptime(
                    article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                )
            except ValueError:
                pass

        news = NewsArticle(
            ticker       = ticker,
            title        = article["title"][:500],
            summary      = article.get("description") or article.get("content"),
            url          = article["url"][:1000],
            source       = article.get("source", {}).get("name"),
            published_at = published_at,
        )

        try:
            db.add(news)
            db.flush()
            inserted += 1
        except IntegrityError:
            db.rollback()
            skipped += 1

    db.commit()
    return {"inserted": inserted, "skipped": skipped}


# Map ticker to full company name for better news search results
COMPANY_NAMES = {
    "NVDA":  "NVIDIA",
    "AAPL":  "Apple",
    "TSLA":  "Tesla",
    "MSFT":  "Microsoft",
    "AMZN":  "Amazon",
    "GOOGL": "Google",
    "META":  "Meta",
    "NFLX":  "Netflix",
    "AMD":   "AMD",
    "JPM":   "JPMorgan",
}


def run():
    """
    Fetches news for every company in the database.
    """
    db = SessionLocal()
    total_inserted = 0
    total_skipped  = 0

    try:
        companies = db.query(Company).all()
        print(f"News collector starting. Companies: {len(companies)}")

        for company in companies:
            search_name = COMPANY_NAMES.get(company.ticker, company.name)
            try:
                articles = fetch_news_for_ticker(search_name, company.ticker, days_back=7)
                if not articles:
                    continue
                result = save_articles(db, company.ticker, articles)
                total_inserted += result["inserted"]
                total_skipped  += result["skipped"]
                print(f"  {company.ticker}: inserted={result['inserted']}, skipped={result['skipped']}")
            except Exception as e:
                print(f"  ERROR processing {company.ticker}: {e}")
                db.rollback()
                continue

    finally:
        db.close()

    print(f"\nNews collector done. Total inserted: {total_inserted}, skipped: {total_skipped}")

if __name__ == "__main__":
    run()