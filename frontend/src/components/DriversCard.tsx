import type { Score } from "@/lib/api";

interface Props {
  breakdown: NonNullable<Score["breakdown"]>;
}

function SubScoreRow({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
      <span className="text-sm text-gray-400 capitalize">{label.replace(/_/g, " ")}</span>
      <div className="flex items-center gap-3">
        <div className="w-32 h-1.5 bg-gray-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${color}`}
            style={{ width: `${Math.min(100, value)}%` }}
          />
        </div>
        <span className="text-sm font-mono text-gray-300 w-8 text-right">
          {value.toFixed(0)}
        </span>
      </div>
    </div>
  );
}

export default function DriversCard({ breakdown }: Props) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="grid grid-cols-2 gap-8">
        <div>
          <p className="text-xs text-amber-400 font-medium mb-3 uppercase tracking-wider">
            Hype Drivers
          </p>
          {Object.entries(breakdown.hype_sub_scores || {}).map(([k, v]) => (
            <SubScoreRow key={k} label={k} value={v as number} color="bg-amber-500" />
          ))}
        </div>
        <div>
          <p className="text-xs text-violet-400 font-medium mb-3 uppercase tracking-wider">
            Fundamental Drivers
          </p>
          {Object.entries(breakdown.fund_sub_scores || {}).map(([k, v]) => (
            <SubScoreRow key={k} label={k} value={v as number} color="bg-violet-500" />
          ))}
        </div>
      </div>
    </div>
  );
}