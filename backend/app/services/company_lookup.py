import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import yfinance as yf
from sqlalchemy.orm import Session
from app.models.company import Company
from app.models.financials import Financials
from collectors.stock_collector import fetch_prices_for_ticker, save_prices
from collectors.financials_collector import (
    fetch_financials_for_ticker,
    build_financials_row,
    update_company_info,
)
from datetime import date


def get_or_create_company(db: Session, ticker: str) -> Company | None:
    """
    Look up a company by ticker. If it exists return it.
    If not, fetch from Yahoo Finance, store it, and return it.
    Returns None if the ticker is invalid.
    """
    ticker = ticker.upper().strip()

    # Already in database, return immediately
    existing = db.query(Company).filter(Company.ticker == ticker).first()
    if existing:
        return existing

    print(f"  {ticker} not in DB — fetching from Yahoo Finance...")

    try:
        stock = yf.Ticker(ticker)
        info  = stock.info

        # Yahoo Finance returns mostly empty dict for invalid tickers
        name = info.get("longName") or info.get("shortName")
        if not name:
            print(f"  {ticker} — no data found, invalid ticker")
            return None

        # Create the company record
        company = Company(
            ticker      = ticker,
            name        = name,
            sector      = info.get("sector"),
            industry    = info.get("industry"),
            country     = info.get("country"),
            description = info.get("longBusinessSummary"),
            employees   = info.get("fullTimeEmployees"),
            website     = info.get("website"),
            market_cap  = str(info.get("marketCap", "")),
        )
        db.add(company)
        db.flush()
        print(f"  Created: {ticker} — {name}")

        # Fetch and store 365 days of prices
        price_df = fetch_prices_for_ticker(ticker, days_back=365)
        if not price_df.empty:
            save_prices(db, ticker, price_df)
            print(f"  Stored {len(price_df)} price rows")

        # Fetch and store financials
        fin_data = fetch_financials_for_ticker(ticker)
        fin_row  = build_financials_row(
            ticker      = ticker,
            info        = fin_data["info"],
            period_date = date.today(),
            period_type = "annual",
        )
        db.add(fin_row)

        db.commit()
        print(f"  {ticker} fully loaded")
        return company

    except Exception as e:
        db.rollback()
        print(f"  ERROR loading {ticker}: {e}")
        return None