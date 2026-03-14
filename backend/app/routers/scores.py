from fastapi import APIRouter

router = APIRouter()

@router.get("/{ticker}")
def get_scores(ticker: str):
    return {"ticker": ticker.upper(), "message": "scores ticker"}