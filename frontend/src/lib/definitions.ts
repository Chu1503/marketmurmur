export const DEFINITIONS = {
    // Hype inputs
    news_volume: [
        "How many news articles mentioned this company in the last 7 days",
        "More articles = more buzz",
      ],
      
      sentiment: [
        "Whether the news coverage is positive or negative",
        "Scored from -1 (very negative) to +1 (very positive)",
      ],
      
      hype_keywords: [
        "Count of hype words in headlines (words like surge, revolutionary, breakout, record)",
        "More keywords = more hype language",
      ],
      
      momentum: [
        "How much the stock price has moved in the last 30 days",
        "A rising stock adds to the hype signal",
      ],
  
    // Fundamentals inputs
    revenue_growth: [
        "How fast the company's sales are growing compared to last year",
        "20% means revenue is 20% higher than a year ago",
      ],
      
      net_margin: [
        "Out of every $1 the company earns in revenue, how much is actual profit",
        "25% means $0.25 profit per $1 of sales",
      ],
      
      gross_margin: [
        "How efficiently the company makes its product",
        "Higher is better (software companies often hit 70%+)",
      ],
      
      pe_ratio: [
        "Price-to-Earnings ratio",
        "How much investors pay for $1 of profit",
        "A P/E of 30 means you pay $30 for every $1 earned",
        "Lower generally means better value",
      ],
      
      debt_to_equity: [
        "How much debt the company has compared to its own money",
        "Lower is safer",
        "A score of 1.0 means equal debt and equity",
      ],
      
      earnings_growth: [
        "How fast the company's profits are growing year over year",
        "High earnings growth justifies a higher stock price",
      ],
  
    // Score concepts
    hype_score: [
      "A 0 - 100 score measuring how much media and market attention the company is currently getting",
      "Combines news volume, sentiment, buzz keywords, and price momentum",
    ],
    fund_score: [
      "A 0 - 100 score measuring how strong the company's financial health is",
      "Combines revenue growth, margins, valuation, and debt levels",
    ],
    hype_gap: [
      "Hype Score minus Fundamentals Score. Positive means more hype than fundamentals justify",
      "Negative means strong fundamentals with less attention",
    ],
  } as const;