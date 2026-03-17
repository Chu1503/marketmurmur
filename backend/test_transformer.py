import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.services.sentiment import run_full_sentiment_pipeline
from app.services.hype_score import run_all_hype_scores
from app.services.competitor import get_competitor_comparison

db = SessionLocal()

print("Step 1: Running sentiment pipeline")
run_full_sentiment_pipeline(db)

print()
print("Step 2: Computing all Hype Scores")
results = run_all_hype_scores(db)

print()
print("Step 3: NVDA competitor comparison")
comparison = get_competitor_comparison(db, "NVDA")
for company in comparison["comparisons"]:
    print(f"  {company['ticker']:6} | "
          f"PE: {str(company.get('pe_ratio', 'N/A')):8} | "
          f"Margin: {str(company.get('net_margin', 'N/A')):8} | "
          f"Hype: {str(company.get('hype_score', 'N/A')):6} | "
          f"Fund: {str(company.get('fund_score', 'N/A')):6} | "
          f"Label: {company.get('label', 'N/A')}")

print()
print("Hype Score Summary")
for r in sorted(results, key=lambda x: x.get("hype_gap", 0), reverse=True):
    print(f"  {r['ticker']:6} | "
          f"Hype: {r['hype_score']:5.1f} | "
          f"Fund: {r['fund_score']:5.1f} | "
          f"Gap: {r['hype_gap']:+6.1f} | "
          f"{r['label']}")

db.close()