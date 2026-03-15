import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import SessionLocal
from app.models.company import Company

COMPANIES = [
    {"ticker": "NVDA",  "name": "NVIDIA Corporation",         "sector": "Technology",        "industry": "Semiconductors"},
    {"ticker": "AAPL",  "name": "Apple Inc.",                  "sector": "Technology",        "industry": "Consumer Electronics"},
    {"ticker": "TSLA",  "name": "Tesla Inc.",                  "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
    {"ticker": "MSFT",  "name": "Microsoft Corporation",       "sector": "Technology",        "industry": "Software"},
    {"ticker": "AMZN",  "name": "Amazon.com Inc.",             "sector": "Consumer Cyclical", "industry": "Internet Retail"},
    {"ticker": "GOOGL", "name": "Alphabet Inc.",               "sector": "Technology",        "industry": "Internet Content"},
    {"ticker": "META",  "name": "Meta Platforms Inc.",         "sector": "Technology",        "industry": "Internet Content"},
    {"ticker": "NFLX",  "name": "Netflix Inc.",                "sector": "Technology",        "industry": "Entertainment"},
    {"ticker": "AMD",   "name": "Advanced Micro Devices Inc.", "sector": "Technology",        "industry": "Semiconductors"},
    {"ticker": "JPM",   "name": "JPMorgan Chase & Co.",        "sector": "Financial",         "industry": "Banks"},
]


def seed():
    db = SessionLocal()
    added = 0
    skipped = 0

    try:
        for data in COMPANIES:
            existing = db.query(Company).filter(Company.ticker == data["ticker"]).first()
            if existing:
                print(f"  Skipping {data['ticker']} - already exists")
                skipped += 1
                continue

            company = Company(**data)
            db.add(company)
            added += 1
            print(f"  Added {data['ticker']} - {data['name']}")

        db.commit()
        print(f"\nDone. Added: {added}, Skipped: {skipped}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()