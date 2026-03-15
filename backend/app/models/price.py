from sqlalchemy import Column, String, Integer, Float, Date, DateTime, func, UniqueConstraint
from app.database import Base

class Price(Base):
    __tablename__ = "prices"

    id         = Column(Integer, primary_key=True, index=True)
    ticker     = Column(String(10), nullable=False, index=True)
    date       = Column(Date, nullable=False, index=True)
    open       = Column(Float)
    high       = Column(Float)
    low        = Column(Float)
    close      = Column(Float, nullable=False)
    volume     = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("ticker", "date", name="uq_prices_ticker_date"),
    )

    def __repr__(self):
        return f"<Price {self.ticker} {self.date} close={self.close}>"