import AboutModal from "@/components/AboutModal";
import SearchBar from "@/components/SearchBar";
import { fetchLeaderboard } from "@/lib/api";
import type { LeaderboardEntry } from "@/lib/api";
import { clsx } from "clsx";
import Image from "next/image";

export default async function HomePage() {
  let leaderboard: LeaderboardEntry[] = [];
  try {
    leaderboard = await fetchLeaderboard();
  } catch {}

  return (
    <div className="space-y-12">
      <div className="text-center space-y-4 pt-8">
        <Image
          src="/marketmurmur-logo.png"
          alt="MarketMurmur"
          width={120}
          height={120}
          className="w-24 h-24 object-contain mx-auto"
          priority
        />
        <h1 className="text-4xl font-bold text-white">
          <span className="text-amber-400">Market</span>
          <span className="text-violet-400">Murmur</span>
        </h1>
        <p className="text-gray-400 text-lg max-w-3xl mx-auto">
          A market intelligence platform that tracks public companies and shows
          you whether the media hype around them matches their actual financial
          performance
        </p>
        <AboutModal />
        <SearchBar />
      </div>

      {leaderboard.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-white mb-4">
            Hype Gap Leaderboard
            <span className="text-sm font-normal text-gray-500 ml-2">
              (sorted by most overhyped)
            </span>
          </h2>
          <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-500 uppercase tracking-wider border-b border-gray-800 bg-gray-900/50">
                  <th className="text-left px-4 py-3">Company</th>
                  <th className="text-right px-4 py-3">Hype</th>
                  <th className="text-right px-4 py-3">Fundamentals</th>
                  <th className="text-right px-4 py-3">Gap</th>
                  <th className="text-right px-4 py-3">Verdict</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.map((entry) => (
                  <tr
                    key={entry.ticker}
                    className="border-b border-gray-800/50 last:border-0 hover:bg-gray-800/30 transition-colors"
                  >
                    <td className="px-4 py-3">
                      <a
                        href={`/company/${entry.ticker}`}
                        className="flex items-center gap-3 group"
                      >
                        <span className="font-mono font-semibold text-white group-hover:text-violet-400 transition-colors">
                          {entry.ticker}
                        </span>
                        <span className="text-gray-500 text-xs hidden sm:block">
                          {entry.name}
                        </span>
                      </a>
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-amber-400">
                      {entry.hype_score.toFixed(1)}
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-violet-400">
                      {entry.fund_score.toFixed(1)}
                    </td>
                    <td
                      className={clsx(
                        "px-4 py-3 text-right font-mono font-semibold",
                        entry.hype_gap > 20 && "text-red-400",
                        entry.hype_gap < -20 && "text-blue-400",
                        Math.abs(entry.hype_gap) <= 20 && "text-emerald-400"
                      )}
                    >
                      {entry.hype_gap > 0 ? "+" : ""}
                      {entry.hype_gap.toFixed(1)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span
                        className={clsx(
                          "text-xs px-2 py-0.5 rounded-full font-medium",
                          entry.label === "Overhyped" &&
                            "bg-red-900/50 text-red-300",
                          entry.label === "Aligned" &&
                            "bg-emerald-900/50 text-emerald-300",
                          entry.label === "Undervalued" &&
                            "bg-blue-900/50 text-blue-300"
                        )}
                      >
                        {entry.label}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
