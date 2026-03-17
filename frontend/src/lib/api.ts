const API_URL = typeof window === "undefined"
  ? (process.env.API_URL || "http://127.0.0.1:8000")
  : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");

export interface Company {
  ticker:      string;
  name:        string;
  sector:      string;
  industry:    string;
  description: string;
  employees:   number;
  website:     string;
  market_cap:  string;
}

export interface PricePoint {
  date:           string;
  close:          number;
  volume:         number | null;
  rolling_7d_avg: number | null;
}

export interface NewsArticle {
  title:               string;
  source:              string;
  published_at:        string;
  url:                 string | null;
  sentiment_label:     string | null;
  sentiment_compound:  number | null;
}

export interface ScoreBreakdown {
  hype_inputs:      Record<string, number>;
  hype_sub_scores:  Record<string, number>;
  fund_inputs:      Record<string, number>;
  fund_sub_scores:  Record<string, number>;
}

export interface Score {
  hype_score:    number;
  fund_score:    number;
  hype_gap:      number;
  label:         string;
  breakdown:     ScoreBreakdown;
  calculated_at: string;
}

export interface Momentum {
  current_price:  number;
  momentum_30d:   number;
  volatility_30d: number;
  avg_volume_30d: number;
}

export interface CompetitorRow {
  ticker:              string;
  name?:               string;
  current_price?:      number;
  pe_ratio?:           number;
  net_margin?:         number;
  revenue_growth_yoy?: number;
  hype_score?:         number;
  fund_score?:         number;
  hype_gap?:           number;
  label?:              string;
  error?:              string;
}

export interface DashboardData {
  company:     Company;
  score:       Score | null;
  momentum:    Momentum;
  prices:      PricePoint[];
  news:        NewsArticle[];
  competitors: CompetitorRow[];
}

export interface LeaderboardEntry {
  ticker:     string;
  name:       string;
  hype_score: number;
  fund_score: number;
  hype_gap:   number;
  label:      string;
}

export async function fetchDashboard(ticker: string): Promise<DashboardData> {
  const res = await fetch(`${API_URL}/api/v1/dashboard/${ticker}`, {
    next: { revalidate: 300 },
  });
  if (!res.ok) {
    if (res.status === 404) throw new Error(`Company "${ticker}" not found`);
    throw new Error("Failed to fetch dashboard data");
  }
  return res.json();
}

export async function fetchLeaderboard(): Promise<LeaderboardEntry[]> {
  const res = await fetch(`${API_URL}/api/v1/scores/`, {
    next: { revalidate: 300 },
  });
  if (!res.ok) throw new Error("Failed to fetch leaderboard");
  return res.json();
}

export async function fetchCompanies(): Promise<Company[]> {
  const res = await fetch(`${API_URL}/api/v1/companies/`, {
    next: { revalidate: 3600 },
  });
  if (!res.ok) throw new Error("Failed to fetch companies");
  return res.json();
}