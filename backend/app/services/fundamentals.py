import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from app.services.data_transformer import get_clean_financials


def normalize(value: float, low: float, high: float,
              invert: bool = False) -> float:
    """
    Map a value to a 0-100 scale given a low and high reference point.

    Examples:
      normalize(0.25, 0, 0.5)  → 50  (25% margin out of 50% max = halfway)
      normalize(50, 0, 100)    → 50
      normalize(200, 0, 500, invert=True) → 60  (lower PE is better)

    Values outside [low, high] are clipped to 0 or 100.
    invert=True means lower raw value = higher score (used for PE ratio,
    debt-to-equity where lower is better).
    """
    if value is None:
        return 50.0

    value = max(low, min(high, value))

    ratio = (value - low) / (high - low) if high != low else 0.5

    if invert:
        ratio = 1.0 - ratio

    return round(ratio * 100, 2)


def compute_fundamentals_score(db: Session, ticker: str) -> dict:
    """
    Compute the Fundamentals Score (0-100) for a ticker.

    The score is a weighted average of 6 sub-scores derived from
    publicly available financial metrics. Higher = stronger fundamentals.

    Sub-scores and their weights:
      - Revenue growth    20%  (how fast is the business growing?)
      - Net margin        20%  (how profitable per dollar of revenue?)
      - Gross margin      15%  (how efficient is the core business?)
      - PE ratio          20%  (is the valuation sane? lower PE = better)
      - Debt to equity    15%  (how leveraged is the balance sheet?)
      - Earnings growth   10%  (are profits growing?)
    """
    metrics = get_clean_financials(db, ticker)

    if not metrics:
        return {
            "fund_score":   50.0,
            "sub_scores":   {},
            "inputs":       {},
            "error":        "No financials data found",
        }

    # Revenue growth: -10% (shrinking) to +100% (hyper-growth)
    # 0% growth = 9 points, 30% growth = 39 points, 73% growth = 80 points
    rev_growth_score = normalize(
        metrics.get("revenue_growth_yoy"), low=-0.10, high=1.00
    )

    # Net margin: -20% (losing money) to +40% (very profitable)
    # 0% = 33, 10% = 58, 25% = 75, 55% = 100 (clipped)
    net_margin_score = normalize(
        metrics.get("net_margin"), low=-0.20, high=0.40
    )

    # Gross margin: 0% to 80% (software companies hit 70-80%)
    gross_margin_score = normalize(
        metrics.get("gross_margin"), low=0.0, high=0.80
    )

    # PE ratio: lower is better (inverted)
    # PE of 15 = great (score ~77), PE of 30 = ok (score ~50),
    # PE of 100+ = expensive (score ~0), missing PE = 50 (neutral)
    pe = metrics.get("pe_ratio")
    if pe is None or pe <= 0:
        pe_score = 50.0     # neutral for companies with no earnings
    else:
        pe_score = normalize(pe, low=5, high=60, invert=True)

    dte = metrics.get("debt_to_equity")
    if dte is None:
        dte_score = 50.0
    else:
        dte_score = normalize(dte, low=0, high=3.0, invert=True)

    earn_growth_score = normalize(
        metrics.get("earnings_growth_yoy"), low=-0.50, high=1.00
    )

    weights = {
        "revenue_growth":  0.20,
        "net_margin":      0.20,
        "gross_margin":    0.15,
        "pe_ratio":        0.20,
        "debt_to_equity":  0.15,
        "earnings_growth": 0.10,
    }

    sub_scores = {
        "revenue_growth":  rev_growth_score,
        "net_margin":      net_margin_score,
        "gross_margin":    gross_margin_score,
        "pe_ratio":        pe_score,
        "debt_to_equity":  dte_score,
        "earnings_growth": earn_growth_score,
    }

    fund_score = sum(
        sub_scores[k] * weights[k] for k in weights
    )

    return {
        "fund_score": round(fund_score, 2),
        "sub_scores": sub_scores,
        "inputs":     metrics,
    }