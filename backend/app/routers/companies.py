from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.company import Company
from app.services.competitor import get_competitor_comparison
from app.services.company_lookup import get_or_create_company

router = APIRouter()

@router.get("/")
def list_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).order_by(Company.ticker).all()
    return [
        {
            "ticker":   c.ticker,
            "name":     c.name,
            "sector":   c.sector,
            "industry": c.industry,
            "website":  c.website,
        }
        for c in companies
    ]

@router.get("/{ticker}")
def get_company(ticker: str, db: Session = Depends(get_db)):
    ticker  = ticker.upper()
    company = get_or_create_company(db, ticker)

    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{ticker}' not found")

    return {
        "ticker":      company.ticker,
        "name":        company.name,
        "sector":      company.sector,
        "industry":    company.industry,
        "country":     company.country,
        "description": company.description,
        "employees":   company.employees,
        "website":     company.website,
        "market_cap":  company.market_cap,
    }


@router.get("/{ticker}/compare")
def compare_company(ticker: str, db: Session = Depends(get_db)):
    ticker  = ticker.upper()
    company = get_or_create_company(db, ticker)

    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{ticker}' not found")

    return get_competitor_comparison(db, ticker)