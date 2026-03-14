from fastapi import APIRouter

router = APIRouter()

@router.get("/{ticker}")
def get_prices(ticker: str):
    return {"ticker": ticker.upper(), "message": "prices ticker"}