import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from app.services.fundamentals import compute_fundamentals_score
from app.services.hype_score import compute_hype_score
from app.services.data_transformer import get_clean_financials, get_price_momentum
from app.models.company import Company
from app.models.scores import HypeScore


# Define peer groups — companies that compete in the same space
PEER_GROUPS = {
    "NVDA":  ["AMD",   "INTC", "QCOM"],
    "AMD":   ["NVDA",  "INTC", "QCOM"],
    "AAPL":  ["MSFT",  "GOOGL", "META"],
    "MSFT":  ["AAPL",  "GOOGL", "AMZN"],
    "TSLA":  ["AMZN",  "MSFT", "AAPL"],
    "AMZN":  ["MSFT",  "GOOGL", "META"],
    "GOOGL": ["META",  "MSFT", "AMZN"],
    "META":  ["GOOGL", "SNAP", "AMZN"],
    "NFLX":  ["DIS",   "AMZN", "AAPL"],
    "JPM":   ["BAC",   "WFC",  "GS"],
}


def get_company_snapshot(db: Session, ticker: str) -> dict:
    company = db.query(Company).filter(Company.ticker == ticker).first()

    if not company:
        return {"ticker": ticker, "error": "Not in database"}

    latest_hype = (
        db.query(HypeScore)
        .filter(HypeScore.ticker == ticker)
        .order_by(HypeScore.calculated_at.desc())
        .first()
    )

    financials = get_clean_financials(db, ticker)
    momentum   = get_price_momentum(db, ticker)

    snapshot = {
        "ticker":        ticker,
        "name":          company.name,
        "sector":        company.sector,
        "industry":      company.industry,

        # Price
        "current_price": momentum.get("current_price"),
        "momentum_30d":  momentum.get("momentum_30d"),

        # Key Financials
        "pe_ratio":           financials.get("pe_ratio"),
        "net_margin":         financials.get("net_margin"),
        "revenue_growth_yoy": financials.get("revenue_growth_yoy"),
        "gross_margin":       financials.get("gross_margin"),
        "debt_to_equity":     financials.get("debt_to_equity"),

        # Scores
        "hype_score": latest_hype.hype_score if latest_hype else None,
        "fund_score": latest_hype.fund_score if latest_hype else None,
        "hype_gap":   latest_hype.hype_gap   if latest_hype else None,
        "label":      latest_hype.label       if latest_hype else None,
    }

    return snapshot


def get_competitor_comparison(db: Session, ticker: str) -> dict:
    """
    Return a comparison table for a ticker and its peers.
    The target company is always first in the list.
    """
    peers = PEER_GROUPS.get(ticker.upper(), [])

    all_tickers  = [ticker.upper()] + peers
    snapshots    = []

    for t in all_tickers:
        snapshot = get_company_snapshot(db, t)
        snapshots.append(snapshot)

    return {
        "target":      ticker.upper(),
        "peers":       peers,
        "comparisons": snapshots,
    }