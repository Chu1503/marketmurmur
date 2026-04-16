# MarketMurmur

MarketMurmur is a market intelligence platform that helps users see whether a company's public buzz actually matches its financial strength.

Instead of just showing stock prices or headlines, it brings together market data, financial metrics, and news sentiment into one dashboard and calculates a custom **Hype vs Fundamentals** signal. The goal is simple: help users quickly spot companies that may be **overhyped, fairly priced, or undervalued**.

## Why I built this

Retail investors and finance enthusiasts see a lot of noise every day: viral headlines, strong opinions, sudden price moves, and endless market hype. What is usually missing is a structured way to compare that attention with what the company's financials actually look like.

MarketMurmur was built to close that gap.

It tracks public companies, measures how much attention they are getting, compares that against financial performance, and presents the result in a way that is visual, fast, and easy to understand.

## What the platform does

MarketMurmur lets users:

- Search for a public company by ticker
- View a full analytics dashboard for that company
- Track recent stock price movement
- Read recent news with sentiment labels
- Compare media hype against real financial metrics
- See whether a stock looks **Overhyped**, **Aligned**, or **Undervalued**
- Compare companies side by side on a leaderboard

## Core idea: Hype vs Fundamentals

The main idea behind MarketMurmur is simple:

A company can get a lot of public attention, but that does not always mean the underlying business is equally strong.

So the platform calculates two separate scores:

### Hype Score
This measures how much market attention and excitement a company is getting.

It is based on:
- News volume
- Average news sentiment
- Hype-related keywords in headlines
- 30-day stock price momentum

### Fundamentals Score
This measures how strong the business actually looks based on key financial metrics.

It is based on:
- Revenue growth
- Net margin
- Gross margin
- P/E ratio
- Debt-to-equity ratio
- Earnings growth

### Final label
The platform compares the two scores and assigns a category:

- **Overhyped**: hype is much higher than fundamentals
- **Aligned**: hype and fundamentals are reasonably close
- **Undervalued**: fundamentals are stronger than the current hype

## Features

### 1. Company search and dashboard
Users can search any supported public company ticker and open a full dashboard page with all major signals in one place.

### 2. Price history and trend analysis
The dashboard shows recent stock price movement along with rolling averages to help users understand short-term trend behavior.

### 3. News sentiment analysis
Recent news articles are collected and scored for sentiment, helping users understand whether current coverage is positive, neutral, or negative.

### 4. Hype vs Fundamentals scoring
Each company gets a custom score breakdown that turns raw data into a much more usable investment signal.

### 5. Leaderboard
The homepage ranks tracked companies by hype gap so users can quickly scan for outliers.

### 6. Auto-discovery for new tickers
If a user searches for a company that is not already stored, the backend can fetch its historical prices, financial data, and recent news automatically, then build the dashboard on demand.

## Example user flow

1. User lands on the homepage
2. They see a leaderboard of tracked companies
3. They search a ticker or click a company
4. The platform loads the company dashboard
5. The user sees:
   - company overview
   - stock price history
   - sentiment trends
   - recent headlines
   - Hype Score
   - Fundamentals Score
   - final label
   - competitor comparison

## Tech stack

## Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS
- Recharts

## Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pandas
- VADER Sentiment
- Requests
- yfinance

## Infrastructure / orchestration
- Docker Compose
- n8n
- Supabase for production Postgres
- Render for backend deployment

## System design overview

The project is split into four main parts:

### Frontend
The frontend is built with Next.js and Tailwind CSS. It renders the dashboard, leaderboard, charts, metric cards, news cards, and comparison tables.

It uses server-side data fetching and timed revalidation so pages stay fresh without constant client-side polling.

### Backend API
The backend is built with FastAPI and exposes endpoints for:
- company dashboard data
- leaderboard data
- analytics results
- webhook triggers for scheduled jobs

The most important endpoint returns an aggregated company dashboard payload so the frontend can fetch everything in one request.

### Data pipeline
Scheduled workflows collect:
- stock prices
- news articles
- financial metrics

These jobs run automatically on a schedule through n8n and write the results into PostgreSQL.

### Analytics layer
The analytics pipeline processes raw market and news data, performs sentiment analysis, calculates normalized metrics, and generates the final Hype Score, Fundamentals Score, and hype gap label.