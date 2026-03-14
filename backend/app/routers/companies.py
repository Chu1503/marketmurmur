from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_companies():
    return {"message": "companies endpoint"}

@router.get("/{ticker}")
def get_company(ticker: str):
    return {"ticker": ticker.upper(), "message": "companies ticker"}