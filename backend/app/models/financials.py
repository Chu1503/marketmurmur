from sqlalchemy import Column, String, Integer, Float, Date, DateTime, func, UniqueConstraint
from app.database import Base

class Financials(Base):
    __tablename__ = "financials"

    id                  = Column(Integer, primary_key=True, index=True)
    ticker              = Column(String(10), nullable=False, index=True)
    period_date         = Column(Date, nullable=False)  # quarter end date
    period_type         = Column(String(10), default="quarterly")   # quarterly / annual

    revenue             = Column(Float)
    gross_profit        = Column(Float)
    operating_income    = Column(Float)
    net_income          = Column(Float)
    eps                 = Column(Float) # earnings per share

    gross_margin        = Column(Float)
    operating_margin    = Column(Float)
    net_margin          = Column(Float)

    pe_ratio            = Column(Float) # price to earnings
    pb_ratio            = Column(Float) # price to book
    ps_ratio            = Column(Float) # price to sales

    total_debt          = Column(Float)
    total_cash          = Column(Float)
    debt_to_equity      = Column(Float)

    revenue_growth_yoy  = Column(Float)
    earnings_growth_yoy = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("ticker", "period_date", "period_type",
                         name="uq_financials_ticker_period"),
    )

    def __repr__(self):
        return f"<Financials {self.ticker} {self.period_date}>"