import { fetchDashboard } from "@/lib/api";
import KPICard from "@/components/KPICard";
import StockChart from "@/components/StockChart";
import HypeGauge from "@/components/HypeGauge";
import NewsCard from "@/components/NewsCard";
import CompetitorTable from "@/components/CompetitorTable";
import { notFound } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import DriversCard from "@/components/DriversCard";

interface Props {
  params: Promise<{ ticker: string }>;
}

export default async function CompanyPage({ params }: Props) {
  const { ticker: rawTicker } = await params;
  const ticker = rawTicker.toUpperCase();

  let data;
  try {
    data = await fetchDashboard(ticker);
  } catch (e: any) {
    if (e.message?.includes("not found")) notFound();
    throw e;
  }

  const { company, score, momentum, prices, news, competitors } = data;

  const pctChange = momentum?.momentum_30d
    ? `${(momentum.momentum_30d * 100).toFixed(2)}%`
    : "—";
  const trend = momentum?.momentum_30d
    ? momentum.momentum_30d >= 0
      ? "up"
      : "down"
    : "neutral";

  return (
    <div className="space-y-6">
      <a
        href="/"
        className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Home
      </a>

      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-white font-mono">
              {ticker}
            </h1>

            {score && (
              <span
                className={[
                  "px-3 py-1 rounded-full text-sm font-semibold",
                  score.label === "Overhyped"
                    ? "bg-red-900/50 text-red-300 border border-red-800"
                    : "",
                  score.label === "Aligned"
                    ? "bg-emerald-900/50 text-emerald-300 border border-emerald-800"
                    : "",
                  score.label === "Undervalued"
                    ? "bg-blue-900/50 text-blue-300 border border-blue-800"
                    : "",
                ].join(" ")}
              >
                {score.label}
              </span>
            )}
          </div>

          <p className="text-gray-400 mt-1">{company.name}</p>

          <p className="text-xs text-gray-600 mt-0.5">
            {company.sector} · {company.industry}
            {company.employees
              ? ` · ${company.employees.toLocaleString()} employees`
              : ""}
          </p>
        </div>

        {company.website && (
          <a
            href={company.website}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-violet-400 hover:text-violet-300 transition-colors"
          >
            {company.website.replace("https://", "")} ↗
          </a>
        )}
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <KPICard
          label="Current price"
          value={
            momentum?.current_price != null
              ? `$${momentum.current_price.toFixed(2)}`
              : "—"
          }
          accent
        />

        <KPICard label="30d momentum" value={pctChange} trend={trend} />

        <KPICard
          label="Volatility (ann.)"
          value={
            momentum?.volatility_30d != null
              ? `${(momentum.volatility_30d * 100).toFixed(1)}%`
              : "—"
          }
        />

        <KPICard
          label="Avg daily volume"
          value={
            momentum?.avg_volume_30d != null
              ? `${(momentum.avg_volume_30d / 1_000_000).toFixed(1)}M`
              : "—"
          }
        />
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 items-stretch">
          <div className="lg:col-span-2">
            <StockChart prices={prices} ticker={ticker} />
          </div>
          <div>
            {score ? (
              <HypeGauge score={score} />
            ) : (
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 text-gray-500 text-sm h-full flex items-center justify-center">
                No score computed yet
              </div>
            )}
          </div>
        </div>

        {score?.breakdown && <DriversCard breakdown={score.breakdown} />}
      </div>

      {company.description && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="font-semibold text-white mb-2">About</h3>
          <p className="text-sm text-gray-400 leading-relaxed line-clamp-4">
            {company.description}
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <NewsCard articles={news} />
        <CompetitorTable competitors={competitors} targetTicker={ticker} />
      </div>
    </div>
  );
}
