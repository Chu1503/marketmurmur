from sqlalchemy import Column, String, Integer, Float, Text, DateTime, func, UniqueConstraint
from app.database import Base

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id              = Column(Integer, primary_key=True, index=True)
    ticker          = Column(String(10), nullable=False, index=True)
    title           = Column(String(500), nullable=False)
    summary         = Column(Text)
    url             = Column(String(1000))
    source          = Column(String(255))
    published_at    = Column(DateTime(timezone=True), index=True)

    sentiment_label    = Column(String(20))
    sentiment_compound = Column(Float)
    sentiment_positive = Column(Float)
    sentiment_negative = Column(Float)
    sentiment_neutral  = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("ticker", "url", name="uq_news_ticker_url"),
    )

    def __repr__(self):
        return f"<NewsArticle {self.ticker} '{self.title[:40]}...'>"