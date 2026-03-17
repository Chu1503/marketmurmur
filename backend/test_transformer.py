import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.services.data_transformer import (
    get_price_momentum,
    get_news_buzz_metrics,
    get_clean_financials,
)

db = SessionLocal()

print("NVDA Price Momentum")
print(get_price_momentum(db, "NVDA"))

print()
print("NVDA News Buzz")
print(get_news_buzz_metrics(db, "NVDA"))

print()
print("NVDA Financials")
print(get_clean_financials(db, "NVDA"))

db.close()
print("\nAll transformer tests passed.")