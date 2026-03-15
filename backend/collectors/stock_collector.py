import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models.company import Company
from app.models.price import Price


def fetch_prices_for_ticker(ticker: str, days_back: int = 365) -> pd.DataFrame:
    """
    Fetch historical daily prices from Yahoo Finance.
    Returns a DataFrame with columns: date, open, high, low, close, volume
    """
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days_back)

    print(f"  Fetching prices for {ticker} ({days_back} days)...")

    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date.strftime("%Y-%m-%d"),
                       end=end_date.strftime("%Y-%m-%d"))

    if df.empty:
        print(f"  WARNING: No price data returned for {ticker}")
        return pd.DataFrame()

    df = df.reset_index()

    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
    df.columns = ["date", "open", "high", "low", "close", "volume"]

    df["date"] = pd.to_datetime(df["date"]).dt.date

    df = df.dropna(subset=["close"])

    print(f"  Got {len(df)} price rows for {ticker}")
    return df


def save_prices(db, ticker: str, df: pd.DataFrame) -> dict:
    inserted = 0
    skipped = 0

    for _, row in df.iterrows():
        price = Price(
            ticker=ticker,
            date=row["date"],
            open=float(row["open"])   if pd.notna(row["open"])   else None,
            high=float(row["high"])   if pd.notna(row["high"])   else None,
            low=float(row["low"])     if pd.notna(row["low"])    else None,
            close=float(row["close"]),
            volume=float(row["volume"]) if pd.notna(row["volume"]) else None,
        )
        try:
            db.add(price)
            db.flush()   # sends to DB but doesn't commit yet
            inserted += 1
        except IntegrityError:
            db.rollback()   # undo just this row
            skipped += 1

    db.commit()
    return {"inserted": inserted, "skipped": skipped}


def run():
    """
    Called by n8n, run_collectors.py, or directly.
    Fetches prices for every company in the database.
    """
    db = SessionLocal()
    total_inserted = 0
    total_skipped = 0

    try:
        companies = db.query(Company).all()
        tickers = [c.ticker for c in companies]
        print(f"Stock collector starting. Tickers: {tickers}")

        for ticker in tickers:
            try:
                df = fetch_prices_for_ticker(ticker, days_back=365)
                if df.empty:
                    continue
                result = save_prices(db, ticker, df)
                total_inserted += result["inserted"]
                total_skipped  += result["skipped"]
                print(f"  {ticker}: inserted={result['inserted']}, skipped={result['skipped']}")
            except Exception as e:
                print(f"  ERROR processing {ticker}: {e}")
                db.rollback()
                continue

    finally:
        db.close()

    print(f"\nStock collector done. Total inserted: {total_inserted}, skipped: {total_skipped}")


if __name__ == "__main__":
    run()