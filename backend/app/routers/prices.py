from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.company import Company
from app.services.data_transformer import get_clean_prices, get_price_momentum

router = APIRouter()


@router.get("/{ticker}")
def get_prices(
    ticker: str,
    days:   int = Query(default=90, ge=7, le=365),
    db:     Session = Depends(get_db),
):
    ticker  = ticker.upper()
    company = db.query(Company).filter(Company.ticker == ticker).first()

    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{ticker}' not found")

    df = get_clean_prices(db, ticker, days=days)

    if df.empty:
        return {"ticker": ticker, "days": days, "prices": []}

    prices = []
    for _, row in df.iterrows():
        prices.append({
            "date":           str(row["date"]),
            "open":           round(float(row["open"]),  2) if row["open"]  else None,
            "high":           round(float(row["high"]),  2) if row["high"]  else None,
            "low":            round(float(row["low"]),   2) if row["low"]   else None,
            "close":          round(float(row["close"]), 2),
            "volume":         int(row["volume"])             if row["volume"] else None,
            "rolling_7d_avg": round(float(row["rolling_7d_avg"]), 2)
                              if row["rolling_7d_avg"] and str(row["rolling_7d_avg"]) != "nan"
                              else None,
        })

    momentum = get_price_momentum(db, ticker)

    return {
        "ticker":   ticker,
        "days":     days,
        "momentum": momentum,
        "prices":   prices,
    }