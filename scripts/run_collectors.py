import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from collectors.stock_collector import run as run_stocks
from collectors.news_collector import run as run_news
from collectors.financials_collector import run as run_financials


def run_all():
    print("=" * 50)
    print("MarketMurmur - Manual Collector Run")
    print("=" * 50)

    print("\n[1/3] Running stock collector...")
    run_stocks()

    print("\n[2/3] Running news collector...")
    run_news()

    print("\n[3/3] Running financials collector...")
    run_financials()

    print("\nAll collectors finished.")


if __name__ == "__main__":
    run_all()