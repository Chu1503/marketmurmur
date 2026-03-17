import { clsx } from "clsx";

interface Props {
  label:    string;
  value:    string | number;
  sub?:     string;
  trend?:   "up" | "down" | "neutral";
  accent?:  boolean;
}

export default function KPICard({ label, value, sub, trend, accent }: Props) {
  return (
    <div className={clsx(
      "rounded-xl border p-4 flex flex-col gap-1",
      accent
        ? "bg-violet-950/40 border-violet-800/50"
        : "bg-gray-900 border-gray-800"
    )}>
      <span className="text-xs text-gray-500 uppercase tracking-wider">{label}</span>
      <span className={clsx(
        "text-2xl font-bold",
        trend === "up"   && "text-emerald-400",
        trend === "down" && "text-red-400",
        !trend           && "text-white",
      )}>
        {value}
      </span>
      {sub && <span className="text-xs text-gray-500">{sub}</span>}
    </div>
  );
}