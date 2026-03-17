from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.company import Company
from app.models.scores import HypeScore
from app.services.hype_score import compute_and_save_hype_score
import json
import math

def sanitize_json(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_json(i) for i in obj]
    return obj

router = APIRouter()


@router.get("/{ticker}")
def get_scores(ticker: str, db: Session = Depends(get_db)):
    ticker  = ticker.upper()
    company = db.query(Company).filter(Company.ticker == ticker).first()

    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{ticker}' not found")

    latest = (
        db.query(HypeScore)
        .filter(HypeScore.ticker == ticker)
        .order_by(HypeScore.calculated_at.desc())
        .first()
    )

    if not latest:
        raise HTTPException(
            status_code=404,
            detail=f"No scores computed yet for '{ticker}'. Run the analytics pipeline first."
        )

    breakdown = {}
    if latest.inputs_json:
        try:
            breakdown = json.loads(latest.inputs_json)
        except json.JSONDecodeError:
            breakdown = {}

    return sanitize_json({
        "ticker":         ticker,
        "calculated_at":  str(latest.calculated_at),
        "hype_score":     latest.hype_score,
        "fund_score":     latest.fund_score,
        "hype_gap":       latest.hype_gap,
        "label":          latest.label,
        "breakdown":      breakdown,
    })


@router.post("/{ticker}/refresh")
def refresh_scores(ticker: str, db: Session = Depends(get_db)):
    ticker  = ticker.upper()
    company = db.query(Company).filter(Company.ticker == ticker).first()

    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{ticker}' not found")

    try:
        result = compute_and_save_hype_score(db, ticker)
        return {"status": "ok", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
def get_all_scores(db: Session = Depends(get_db)):
    # Return the latest score for every tracked company
    all_companies = db.query(Company).all()
    results = []

    for company in all_companies:
        latest = (
            db.query(HypeScore)
            .filter(HypeScore.ticker == company.ticker)
            .order_by(HypeScore.calculated_at.desc())
            .first()
        )
        if latest:
            results.append({
                "ticker":     company.ticker,
                "name":       company.name,
                "hype_score": latest.hype_score,
                "fund_score": latest.fund_score,
                "hype_gap":   latest.hype_gap,
                "label":      latest.label,
            })

    results.sort(key=lambda x: x["hype_gap"], reverse=True)
    return results