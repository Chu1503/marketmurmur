from sqlalchemy import Column, String, Integer, Text, DateTime, func
from app.database import Base

class Company(Base):
    __tablename__ = "companies"

    id          = Column(Integer, primary_key=True, index=True)
    ticker      = Column(String(10), unique=True, nullable=False, index=True)
    name        = Column(String(255), nullable=False)
    sector      = Column(String(100))
    industry    = Column(String(100))
    country     = Column(String(100))
    description = Column(Text)
    employees   = Column(Integer)
    website     = Column(String(255))
    market_cap  = Column(String(50))
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Company {self.ticker} - {self.name}>"