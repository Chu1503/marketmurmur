"use client";
import type { Score } from "@/lib/api";
import Tooltip from "@/components/Tooltip";
import { DEFINITIONS } from "@/lib/definitions";

interface Props {
  breakdown: Score["breakdown"];
}

function SubScoreRow({
  label,
  value,
  accent,
}: {
  label: string;
  value: number;
  accent: string;
}) {
  const key = label as keyof typeof DEFINITIONS;
  const definition = DEFINITIONS[key];

  return (
    <div className="flex items-center justify-between py-1 border-b border-gray-800 last:border-0">
      <span className="text-xs text-gray-400 capitalize flex items-center">
        {label.replace(/_/g, " ")}
        {definition && <Tooltip text={definition} />}
      </span>
      <div className="flex items-center gap-2">
        <div className="w-20 h-1.5 bg-gray-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${accent}`}
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

export default function DriversCard({ breakdown }: Props) {
  if (!breakdown) return null;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-amber-400 font-medium mb-2 uppercase tracking-wider">
            Hype drivers
          </p>
          {Object.entries(breakdown.hype_sub_scores || {})
            .filter(([, v]) => (v as number) > 0)
            .map(([k, v]) => (
              <SubScoreRow
                key={k}
                label={k}
                value={v as number}
                accent="bg-amber-500"
              />
            ))}
        </div>
        <div>
          <p className="text-xs text-violet-400 font-medium mb-2 uppercase tracking-wider">
            Fundamental drivers
          </p>
          {Object.entries(breakdown.fund_sub_scores || {})
            .filter(([, v]) => (v as number) > 0)
            .map(([k, v]) => (
              <SubScoreRow
                key={k}
                label={k}
                value={v as number}
                accent="bg-violet-500"
              />
            ))}
        </div>
      </div>
    </div>
  );
}
