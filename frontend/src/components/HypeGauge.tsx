import { clsx } from "clsx";
import type { Score } from "@/lib/api";

interface Props {
  score: Score;
}

function Bar({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs text-gray-400">
        <span>{label}</span>
        <span className="font-mono font-medium text-white">
          {value.toFixed(1)}
        </span>
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

export default function HypeGauge({ score }: Props) {
  const { hype_score, fund_score, hype_gap, label } = score;

  const labelColor = clsx(
    "px-3 py-1 rounded-full text-xs font-semibold",
    label === "Overhyped" && "bg-red-900/50 text-red-300 border border-red-800",
    label === "Aligned" &&
      "bg-emerald-900/50 text-emerald-300 border border-emerald-800",
    label === "Undervalued" &&
      "bg-blue-900/50 text-blue-300 border border-blue-800"
  );

  const gapColor = clsx(
    "text-5xl font-bold font-mono",
    hype_gap > 20 && "text-red-400",
    hype_gap < -20 && "text-blue-400",
    Math.abs(hype_gap) <= 20 && "text-emerald-400"
  );

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 h-full flex flex-col gap-4">
      <h3 className="font-semibold text-white">Hype vs Fundamentals</h3>

      <div className="space-y-3">
        <Bar label="Hype Score" value={hype_score} color="bg-amber-500" />
        <Bar
          label="Fundamentals Score"
          value={fund_score}
          color="bg-violet-500"
        />
      </div>

      <div className="flex-1 bg-gray-800/50 rounded-xl flex flex-col items-center justify-center gap-2 py-4">
        <span className="text-xs text-gray-400 uppercase tracking-widest">
          Hype Gap
        </span>

        <div className="relative flex items-center justify-center">
          <span className="absolute -left-6 text-2xl font-bold font-mono opacity-70">
            {hype_gap > 0 ? "+" : hype_gap < 0 ? "−" : ""}
          </span>
          <span className={gapColor}>{Math.abs(hype_gap).toFixed(1)}</span>
        </div>

        <span className={clsx(labelColor, "text-sm")}>{label}</span>
      </div>
    </div>
  );
}
