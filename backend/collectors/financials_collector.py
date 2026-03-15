import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
import pandas as pd
from datetime import date
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models.company import Company
from app.models.financials import Financials


def safe_float(value) -> float | None:
    try:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_financials_for_ticker(ticker: str) -> dict:
    """
    Fetch financial metrics from Yahoo Finance.
    Returns a dict with all the metrics we care about.
    """
    print(f"  Fetching financials for {ticker}...")

    stock = yf.Ticker(ticker)
    info  = stock.info  # general company info and valuation metrics

    try:
        quarterly = stock.quarterly_income_stmt
    except Exception:
        quarterly = pd.DataFrame()

    result = {
        "info":      info,
        "quarterly": quarterly,
    }
    return result


def build_financials_row(ticker: str, info: dict, period_date: date,
                         period_type: str = "annual") -> Financials:
    """
    Build a Financials model instance from Yahoo Finance info dict.
    """
    revenue    = safe_float(info.get("totalRevenue"))
    gross      = safe_float(info.get("grossProfits"))
    net_income = safe_float(info.get("netIncomeToCommon"))

    gross_margin = None
    net_margin   = None
    if revenue and revenue > 0:
        if gross:
            gross_margin = gross / revenue
        if net_income:
            net_margin = net_income / revenue

    return Financials(
        ticker             = ticker,
        period_date        = period_date,
        period_type        = period_type,

        # Income statement
        revenue            = revenue,
        gross_profit       = gross,
        net_income         = net_income,
        eps                = safe_float(info.get("trailingEps")),

        # Margins
        gross_margin       = gross_margin,
        operating_margin   = safe_float(info.get("operatingMargins")),
        net_margin         = net_margin,

        # Valuation
        pe_ratio           = safe_float(info.get("trailingPE")),
        pb_ratio           = safe_float(info.get("priceToBook")),
        ps_ratio           = safe_float(info.get("priceToSalesTrailing12Months")),

        # Balance sheet
        total_debt         = safe_float(info.get("totalDebt")),
        total_cash         = safe_float(info.get("totalCash")),
        debt_to_equity     = safe_float(info.get("debtToEquity")),

        # Growth
        revenue_growth_yoy  = safe_float(info.get("revenueGrowth")),
        earnings_growth_yoy = safe_float(info.get("earningsGrowth")),
    )


def update_company_info(db, ticker: str, info: dict):
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        return

    company.description = info.get("longBusinessSummary") or company.description
    company.employees   = info.get("fullTimeEmployees")   or company.employees
    company.website     = info.get("website")             or company.website
    company.country     = info.get("country")             or company.country
    company.market_cap  = str(info.get("marketCap", "")) or company.market_cap

    db.flush()


def run():
    """
    Fetches financials for every company in the database.
    """
    db = SessionLocal()
    total_inserted = 0
    total_skipped  = 0

    try:
        companies = db.query(Company).all()
        print(f"Financials collector starting. Companies: {len(companies)}")

        for company in companies:
            try:
                data = fetch_financials_for_ticker(company.ticker)
                info = data["info"]

                period_date = date.today()

                update_company_info(db, company.ticker, info)

                row = build_financials_row(
                    ticker      = company.ticker,
                    info        = info,
                    period_date = period_date,
                    period_type = "annual",
                )

                try:
                    db.add(row)
                    db.flush()
                    total_inserted += 1
                    print(f"  {company.ticker}: saved financials "
                          f"(PE={row.pe_ratio}, margin={row.net_margin})")
                except IntegrityError:
                    db.rollback()
                    total_skipped += 1
                    print(f"  {company.ticker}: skipped (already exists for today)")

                db.commit()

            except Exception as e:
                print(f"  ERROR processing {company.ticker}: {e}")
                db.rollback()
                continue

    finally:
        db.close()

    print(f"\nFinancials collector done. "
          f"Total inserted: {total_inserted}, skipped: {total_skipped}")

if __name__ == "__main__":
    run()