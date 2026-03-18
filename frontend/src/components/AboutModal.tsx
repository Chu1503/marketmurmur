"use client";
import { useState } from "react";
import { X, HelpCircle } from "lucide-react";
import { DEFINITIONS } from "@/lib/definitions";

const SECTIONS = [
  {
    title: "What is the Hype Score?",
    content: DEFINITIONS.hype_score,
  },
  {
    title: "What is the Fundamentals Score?",
    content: DEFINITIONS.fund_score,
  },
  {
    title: "What is the Hype Gap?",
    content: DEFINITIONS.hype_gap,
  },
];

const METRICS = [
  { name: "News Volume", def: DEFINITIONS.news_volume },
  { name: "Sentiment", def: DEFINITIONS.sentiment },
  { name: "Hype Keywords", def: DEFINITIONS.hype_keywords },
  { name: "Momentum", def: DEFINITIONS.momentum },
  { name: "Revenue Growth", def: DEFINITIONS.revenue_growth },
  { name: "Net Margin", def: DEFINITIONS.net_margin },
  { name: "Gross Margin", def: DEFINITIONS.gross_margin },
  { name: "P/E Ratio", def: DEFINITIONS.pe_ratio },
  { name: "Debt to Equity", def: DEFINITIONS.debt_to_equity },
  { name: "Earnings Growth", def: DEFINITIONS.earnings_growth },
];

export default function AboutModal() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-1.5 text-sm text-gray-500
                   hover:text-gray-300 transition-colors"
      >
        <HelpCircle className="w-4 h-4" />
        How it works
      </button>

      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4
                     bg-black/70 backdrop-blur-sm"
          onClick={(e) => e.target === e.currentTarget && setOpen(false)}
        >
          <div
            className="bg-gray-900 border border-gray-800 rounded-2xl
                       w-full max-w-3xl max-h-[85vh] overflow-y-auto shadow-2xl
                       [&::-webkit-scrollbar]:w-1.5
                       [&::-webkit-scrollbar-track]:bg-gray-800
                       [&::-webkit-scrollbar-track]:rounded-full
                       [&::-webkit-scrollbar-thumb]:bg-violet-600
                       [&::-webkit-scrollbar-thumb]:rounded-full
                       [&::-webkit-scrollbar-thumb]:hover:bg-violet-500"
          >
            <div
              className="flex items-center justify-between p-5 border-b border-gray-800
                            sticky top-0 bg-gray-900 rounded-t-2xl"
            >
              <h2 className="text-white font-semibold text-lg">
                How MarketMurmur Works
              </h2>
              <button
                onClick={() => setOpen(false)}
                className="text-gray-500 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-5 space-y-3">
              {SECTIONS.map((s) => (
                <div key={s.title} className="bg-gray-800/40 rounded-xl p-4">
                  <p className="text-sm font-medium text-white mb-1">
                    {s.title}
                  </p>
                  <div className="text-sm text-gray-400 leading-relaxed space-y-1">
                    {Array.isArray(s.content) ? (
                      s.content.map((line, i) => <p key={i}>{line}</p>)
                    ) : (
                      <p>{s.content}</p>
                    )}
                  </div>
                </div>
              ))}

              <div className="bg-gray-800/40 rounded-xl p-4">
                <p className="text-sm font-medium text-white mb-3 text-center">
                  What do the labels mean?
                </p>

                <div className="space-y-3">
                  <div className="flex items-center justify-center gap-3 text-center">
                    <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-red-900/50 text-red-300 shrink-0">
                      Overhyped
                    </span>
                    <p className="text-sm text-gray-400 leading-relaxed">
                      The buzz is much higher than fundamentals justify, could
                      be risky
                    </p>
                  </div>

                  <div className="flex items-center justify-center gap-3 text-center">
                    <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-emerald-900/50 text-emerald-300 shrink-0">
                      Aligned
                    </span>
                    <p className="text-sm text-gray-400 leading-relaxed">
                      Attention roughly matches business quality
                    </p>
                  </div>

                  <div className="flex items-center justify-center gap-3 text-center">
                    <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-blue-900/50 text-blue-300 shrink-0">
                      Undervalued
                    </span>
                    <p className="text-sm text-gray-400 leading-relaxed">
                      Strong fundamentals but not getting much attention
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800/40 rounded-xl p-4">
                <p className="text-sm font-medium text-white mb-4 text-center">
                  Glossary
                </p>

                <div className="space-y-5">
                  {METRICS.map((m) => (
                    <div key={m.name} className="text-center">
                      <p className="text-xs font-semibold text-violet-400 mb-1">
                        {m.name}
                      </p>

                      <div className="text-xs text-gray-400 leading-relaxed space-y-0.5">
                        {Array.isArray(m.def) ? (
                          m.def.map((line, i) => <p key={i}>{line}</p>)
                        ) : (
                          <p>{m.def}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
