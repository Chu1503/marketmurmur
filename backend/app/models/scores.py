from sqlalchemy import Column, String, Integer, Float, Date, DateTime, Text, func, UniqueConstraint
from app.database import Base

class SentimentScore(Base):
    __tablename__ = "sentiment_scores"

    id              = Column(Integer, primary_key=True, index=True)
    ticker          = Column(String(10), nullable=False, index=True)
    date            = Column(Date, nullable=False, index=True)
    article_count   = Column(Integer, default=0)
    avg_compound    = Column(Float)
    positive_count  = Column(Integer, default=0)
    negative_count  = Column(Integer, default=0)
    neutral_count   = Column(Integer, default=0)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("ticker", "date", name="uq_sentiment_ticker_date"),
    )

class HypeScore(Base):
    __tablename__ = "hype_scores"

    id               = Column(Integer, primary_key=True, index=True)
    ticker           = Column(String(10), nullable=False, index=True)
    calculated_at    = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    hype_score       = Column(Float)    # media/sentiment buzz score
    fund_score       = Column(Float)    # fundamentals quality score
    hype_gap         = Column(Float)    # hype_score - fund_score

    label            = Column(String(50))

    inputs_json      = Column(Text)

    def __repr__(self):
        return f"<HypeScore {self.ticker} hype={self.hype_score} fund={self.fund_score} gap={self.hype_gap}>"