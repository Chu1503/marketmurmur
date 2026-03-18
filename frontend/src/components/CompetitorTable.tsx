import { clsx } from "clsx";
import type { CompetitorRow } from "@/lib/api";

interface Props {
  competitors: CompetitorRow[];
  targetTicker: string;
}

function fmt(val: number | undefined | null, decimals = 2, suffix = ""): string {
  if (val == null) return "N/A";
  return `${(val * (suffix === "%" ? 100 : 1)).toFixed(decimals)}${suffix}`;
}

function LabelBadge({ label }: { label?: string }) {
  if (!label) return <span className="text-gray-600">N/A</span>;

  return (
    <span
      className={clsx(
        "text-xs px-2 py-0.5 rounded-full font-medium",
        label === "Overhyped" && "bg-red-900/50 text-red-300",
        label === "Aligned" && "bg-emerald-900/50 text-emerald-300",
        label === "Undervalued" && "bg-blue-900/50 text-blue-300"
      )}
    >
      {label}
    </span>
  );
}

export default function CompetitorTable({ competitors, targetTicker }: Props) {
  const valid = competitors.filter((c) => !c.error);

  if (valid.length === 0) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 text-gray-500 text-sm">
        No competitor data available.
      </div>
    );
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 h-fit">
      <h3 className="font-semibold text-white mb-4">Competitor Comparison</h3>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs text-gray-500 uppercase tracking-wider border-b border-gray-800">
              <th className="text-left pb-2 pr-4">Ticker</th>
              <th className="text-right pb-2 px-3">Price</th>
              <th className="text-right pb-2 px-3">P/E</th>
              <th className="text-right pb-2 px-3">Net margin</th>
              <th className="text-right pb-2 px-3">Rev growth</th>
              <th className="text-right pb-2 px-3">Hype</th>
              <th className="text-right pb-2 px-3">Fund.</th>
              <th className="text-right pb-2 pl-3">Verdict</th>
            </tr>
          </thead>

          <tbody>
            {valid.map((c) => (
              <tr
                key={c.ticker}
                className={clsx(
                  "border-b border-gray-800/50 last:border-0",
                  c.ticker === targetTicker && "bg-violet-950/30"
                )}
              >
                <td className="py-3 pr-4">
                  <a
                    href={`/company/${c.ticker}`}
                    className={clsx(
                      "font-mono font-semibold hover:text-violet-400 transition-colors",
                      c.ticker === targetTicker ? "text-violet-400" : "text-white"
                    )}
                  >
                    {c.ticker}
                  </a>
                </td>

                <td className="py-3 px-3 text-right font-mono text-gray-300">
                  {c.current_price != null ? `$${c.current_price.toFixed(2)}` : "N/A"}
                </td>

                <td className="py-3 px-3 text-right font-mono text-gray-300">
                  {fmt(c.pe_ratio, 1)}
                </td>

                <td className="py-3 px-3 text-right font-mono text-gray-300">
                  {fmt(c.net_margin, 1, "%")}
                </td>

                <td
                  className={clsx(
                    "py-3 px-3 text-right font-mono",
                    (c.revenue_growth_yoy ?? 0) > 0 ? "text-emerald-400" : "text-red-400"
                  )}
                >
                  {fmt(c.revenue_growth_yoy, 1, "%")}
                </td>

                <td className="py-3 px-3 text-right font-mono text-amber-400">
                  {c.hype_score != null ? c.hype_score.toFixed(1) : "N/A"}
                </td>

                <td className="py-3 px-3 text-right font-mono text-violet-400">
                  {c.fund_score != null ? c.fund_score.toFixed(1) : "N/A"}
                </td>

                <td className="py-3 pl-3 text-right">
                  <LabelBadge label={c.label} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}