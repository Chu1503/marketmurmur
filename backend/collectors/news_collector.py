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

GUARDIAN_API_URL = "https://content.guardianapis.com/search"


def fetch_news_for_ticker(company_name: str, ticker: str, days_back: int = 7) -> list:
    """
    Fetch recent news articles from The Guardian API.
    Searches by company name for better results than ticker alone.
    Returns a list of article dicts.
    """
    if not settings.guardian_api_key or settings.guardian_api_key == "your_key_here":
        print(f"  WARNING: GUARDIAN_API_KEY not set. Skipping news for {ticker}")
        return []

    end_date   = datetime.today()
    start_date = end_date - timedelta(days=days_back)

    params = {
        "q":           f'{company_name} OR {ticker}',
        "from-date":   start_date.strftime("%Y-%m-%d"),
        "to-date":     end_date.strftime("%Y-%m-%d"),
        "lang":        "en",
        "order-by":    "newest",
        "page-size":   30,
        "show-fields": "headline,trailText",
        "api-key":     settings.guardian_api_key,
    }

    print(f"  Fetching news for {company_name} ({ticker})...")

    try:
        response = requests.get(GUARDIAN_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        articles = data.get("response", {}).get("results", [])
        print(f"  Got {len(articles)} articles for {ticker}")
        return articles

    except requests.exceptions.RequestException as e:
        print(f"  ERROR fetching news for {ticker}: {e}")
        return []


def save_articles(db, ticker: str, articles: list) -> dict:
    """
    Save Guardian API articles to the database.
    """
    inserted = 0
    skipped  = 0

    for article in articles:
        url = article.get("webUrl")
        if not url:
            continue

        fields    = article.get("fields", {})
        title     = fields.get("headline") or article.get("webTitle", "")[:500]
        summary   = fields.get("trailText")

        published_at = None
        raw_date = article.get("webPublicationDate")
        if raw_date:
            try:
                published_at = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                pass

        news = NewsArticle(
            ticker       = ticker,
            title        = title[:500],
            summary      = summary,
            url          = url[:1000],
            source       = "The Guardian",
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
    "AMD":   "AMD Advanced Micro Devices",
    "JPM":   "JPMorgan",
    "ADBE":  "Adobe",
    "AVGO":  "Broadcom",
    "LULU":  "Lululemon",
    "DOCU":  "DocuSign",
    "TME":   "Tencent Music",
    "Z":     "Zillow",
    "HAL":   "Halliburton",
    "NFE":   "New Fortress Energy",
    "RCAT":  "Red Cat drone",
    "TSAT":  "Telesat satellite",
    "BIAF":  "bioAffinity cancer",
    "AAMI":  "Acadian Asset Management",
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
