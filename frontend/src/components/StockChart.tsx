"use client";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from "recharts";
import type { PricePoint } from "@/lib/api";

interface Props {
  prices:  PricePoint[];
  ticker:  string;
}

export default function StockChart({ prices, ticker }: Props) {
  if (!prices || prices.length === 0) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 h-64
                      flex items-center justify-center text-gray-500">
        No price data available
      </div>
    );
  }

  const formatted = prices.map((p) => ({
    ...p,
    label: new Date(p.date).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
  }));

  const minPrice = Math.min(...prices.map((p) => p.close));
  const maxPrice = Math.max(...prices.map((p) => p.close));
  const padding  = (maxPrice - minPrice) * 0.1;

  const firstClose = prices[0]?.close;
  const lastClose  = prices[prices.length - 1]?.close;
  const isUp       = lastClose >= firstClose;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-white">{ticker} (90 day price)</h3>
        <span className={`text-sm font-mono font-medium
          ${isUp ? "text-emerald-400" : "text-red-400"}`}>
          ${lastClose.toFixed(2)}
        </span>
      </div>

      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={formatted} margin={{ top: 5, right: 5, bottom: 5, left: 0 }}>
          <defs>
            <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor={isUp ? "#10b981" : "#ef4444"} stopOpacity={0.3} />
              <stop offset="95%" stopColor={isUp ? "#10b981" : "#ef4444"} stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis
            dataKey="label"
            tick={{ fill: "#6b7280", fontSize: 11 }}
            tickLine={false}
            interval={Math.floor(prices.length / 6)}
          />
          <YAxis
            domain={[minPrice - padding, maxPrice + padding]}
            tick={{ fill: "#6b7280", fontSize: 11 }}
            tickLine={false}
            tickFormatter={(v) => `$${v.toFixed(0)}`}
            width={55}
          />
          <Tooltip
            contentStyle={{ backgroundColor: "#111827", border: "1px solid #374151",
                            borderRadius: "8px", color: "#fff" }}
            // formatter={(value: number) => [`$${value.toFixed(2)}`, "Close"]}
            labelStyle={{ color: "#9ca3af" }}
          />
          <ReferenceLine y={firstClose} stroke="#4b5563" strokeDasharray="4 4" />
          <Area
            type="monotone"
            dataKey="close"
            stroke={isUp ? "#10b981" : "#ef4444"}
            strokeWidth={2}
            fill="url(#priceGradient)"
            dot={false}
            activeDot={{ r: 4, fill: isUp ? "#10b981" : "#ef4444" }}
          />
          <Area
            type="monotone"
            dataKey="rolling_7d_avg"
            stroke="#8b5cf6"
            strokeWidth={1.5}
            strokeDasharray="4 4"
            fill="none"
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>

      <div className="flex gap-4 mt-2 text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <span className={`w-3 h-0.5 inline-block ${isUp ? "bg-emerald-400" : "bg-red-400"}`} />
          Close price
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-0.5 inline-block bg-violet-400" />
          7-day avg
        </span>
      </div>
    </div>
  );
}