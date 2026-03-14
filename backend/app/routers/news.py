from fastapi import APIRouter

router = APIRouter()

@router.get("/{ticker}")
def get_news(ticker: str):
    return {"ticker": ticker.upper(), "message": "news ticker"}