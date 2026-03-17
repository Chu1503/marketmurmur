import { clsx } from "clsx";
import type { Score } from "@/lib/api";

interface Props { score: Score }

function Bar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-gray-400">
        <span>{label}</span>
        <span className="font-mono font-medium text-white">{value.toFixed(1)}</span>
      </div>
      <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        />
      </div>
    </div>
  );
}

function SubScoreRow({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center justify-between py-1 border-b border-gray-800 last:border-0">
      <span className="text-xs text-gray-400 capitalize">{label.replace(/_/g, " ")}</span>
      <div className="flex items-center gap-2">
        <div className="w-20 h-1.5 bg-gray-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-violet-500 rounded-full"
            style={{ width: `${Math.min(100, value)}%` }}
          />
        </div>
        <span className="text-xs font-mono text-gray-300 w-8 text-right">
          {value.toFixed(0)}
        </span>
      </div>
    </div>
  );
}

export default function HypeGauge({ score }: Props) {
  const { hype_score, fund_score, hype_gap, label, breakdown } = score;

  const labelColor = clsx(
    "px-3 py-1 rounded-full text-sm font-semibold",
    label === "Overhyped"        && "bg-red-900/50 text-red-300 border border-red-800",
    label === "Aligned"          && "bg-emerald-900/50 text-emerald-300 border border-emerald-800",
    label === "Undervalued buzz" && "bg-blue-900/50 text-blue-300 border border-blue-800",
  );

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-white">Hype vs Fundamentals</h3>
        <span className={labelColor}>{label}</span>
      </div>

      <div className="space-y-3">
        <Bar label="Hype Score"         value={hype_score} color="bg-amber-500" />
        <Bar label="Fundamentals Score" value={fund_score} color="bg-violet-500" />
      </div>

      <div className="flex items-center justify-between bg-gray-800/50 rounded-lg px-4 py-3">
        <span className="text-sm text-gray-400">Hype Gap</span>
        <span className={clsx(
          "text-lg font-bold font-mono",
          hype_gap >  20 && "text-red-400",
          hype_gap < -20 && "text-blue-400",
          Math.abs(hype_gap) <= 20 && "text-emerald-400",
        )}>
          {hype_gap > 0 ? "+" : ""}{hype_gap.toFixed(1)}
        </span>
      </div>

      {breakdown && (
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-amber-400 font-medium mb-2 uppercase tracking-wider">
              Hype drivers
            </p>
            {Object.entries(breakdown.hype_sub_scores || {}).map(([k, v]) => (
              <SubScoreRow key={k} label={k} value={v as number} />
            ))}
          </div>
          <div>
            <p className="text-xs text-violet-400 font-medium mb-2 uppercase tracking-wider">
              Fundamental drivers
            </p>
            {Object.entries(breakdown.fund_sub_scores || {}).map(([k, v]) => (
              <SubScoreRow key={k} label={k} value={v as number} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}