import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.services.fundamentals import compute_fundamentals_score, normalize
from app.services.data_transformer import get_news_buzz_metrics, get_price_momentum
from app.models.scores import HypeScore
from app.models.company import Company


def compute_hype_score(db: Session, ticker: str) -> dict:
    """
    Compute the Hype Score (0-100) for a ticker.

    The Hype Score measures how much media/market attention
    a company is currently receiving, normalized to 0-100.

    Inputs and weights:
      - News volume        30%  (how many articles in last 7 days?)
      - Avg sentiment      25%  (how positive is the coverage?)
      - Hype keywords      20%  (how many buzz words in headlines?)
      - Price momentum     25%  (how much has the stock moved recently?)
    """
    buzz    = get_news_buzz_metrics(db, ticker, days=7)
    momentum = get_price_momentum(db, ticker)

    # News volume: 0 articles = 0, 50+ articles = 100
    volume_score = normalize(buzz["article_count"], low=0, high=50)

    # Sentiment: compound ranges -1 to +1, we map -0.5 to +0.5 → 0-100
    # Neutral sentiment (0.0) = 50 points
    sentiment_score = normalize(
        buzz["avg_sentiment"], low=-0.5, high=0.5
    )

    # Hype keywords: 0 = 0 points, 10+ keywords = 100 points
    keyword_score = normalize(buzz["hype_keyword_total"], low=0, high=10)

    # Price momentum: -30% = 0, +30% = 100, flat = 50
    momentum_val = momentum.get("momentum_30d", 0.0) or 0.0
    momentum_score = normalize(momentum_val, low=-0.30, high=0.30)

    weights = {
        "news_volume":  0.30,
        "sentiment":    0.25,
        "hype_keywords": 0.20,
        "momentum":     0.25,
    }

    sub_scores = {
        "news_volume":   volume_score,
        "sentiment":     sentiment_score,
        "hype_keywords": keyword_score,
        "momentum":      momentum_score,
    }

    hype_score = sum(sub_scores[k] * weights[k] for k in weights)

    return {
        "hype_score": round(hype_score, 2),
        "sub_scores": sub_scores,
        "inputs": {
            **buzz,
            **momentum,
        },
    }


def determine_label(hype_gap: float) -> str:
    """
    Convert the numeric hype gap into a human-readable verdict.
    Gap = Hype Score - Fundamentals Score

    > +20  = Overhyped    (buzz far exceeds what fundamentals justify)
    -20 to +20 = Aligned  (attention roughly matches business quality)
    < -20  = Undervalued buzz (strong fundamentals, not getting attention)
    """
    if hype_gap > 20:
        return "Overhyped"
    elif hype_gap < -20:
        return "Undervalued buzz"
    else:
        return "Aligned"


def compute_and_save_hype_score(db: Session, ticker: str) -> dict:
    """
    Compute both Hype Score and Fundamentals Score for a ticker,
    calculate the gap, determine the label, and save to hype_scores table.
    Returns the full result dict.
    """
    print(f"  Computing Hype Score for {ticker}...")

    hype_result = compute_hype_score(db, ticker)
    fund_result = compute_fundamentals_score(db, ticker)

    hype_score = hype_result["hype_score"]
    fund_score = fund_result["fund_score"]
    hype_gap   = round(hype_score - fund_score, 2)
    label      = determine_label(hype_gap)

    all_inputs = {
        "hype_inputs": hype_result["inputs"],
        "hype_sub_scores": hype_result["sub_scores"],
        "fund_inputs": {
            k: v for k, v in fund_result["inputs"].items()
            if k in ["pe_ratio", "net_margin", "gross_margin",
                     "revenue_growth_yoy", "debt_to_equity",
                     "earnings_growth_yoy"]
        },
        "fund_sub_scores": fund_result["sub_scores"],
    }

    score_row = HypeScore(
        ticker        = ticker,
        hype_score    = hype_score,
        fund_score    = fund_score,
        hype_gap      = hype_gap,
        label         = label,
        inputs_json   = json.dumps(all_inputs),
        calculated_at = datetime.utcnow(),
    )

    db.add(score_row)
    db.commit()

    result = {
        "ticker":     ticker,
        "hype_score": hype_score,
        "fund_score": fund_score,
        "hype_gap":   hype_gap,
        "label":      label,
        "breakdown":  all_inputs,
    }

    print(f"  {ticker}: hype={hype_score}, fund={fund_score}, "
          f"gap={hype_gap}, label='{label}'")

    return result


def run_all_hype_scores(db: Session) -> list:
    companies = db.query(Company).all()
    results   = []

    print(f"Computing Hype Scores for {len(companies)} companies...")

    for company in companies:
        try:
            result = compute_and_save_hype_score(db, company.ticker)
            results.append(result)
        except Exception as e:
            print(f"  ERROR computing score for {company.ticker}: {e}")
            db.rollback()
            continue

    return results