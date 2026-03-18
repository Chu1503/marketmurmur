"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search, Loader2 } from "lucide-react";

const POPULAR = ["NVDA", "AAPL", "TSLA", "MSFT", "AMZN", "GOOGL", "META", "AMD", "JPM", "NFLX"];

export default function SearchBar() {
  const [query,   setQuery]   = useState("");
  const [loading, setLoading] = useState(false);
  const router                = useRouter();

  function navigate(ticker: string) {
    const t = ticker.trim().toUpperCase();
    if (!t || loading) return;
    setLoading(true);
    router.push(`/company/${t}`);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    navigate(query);
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        {loading
          ? <Loader2 className="absolute left-4 top-1/2 -translate-y-1/2 text-violet-400 w-5 h-5 animate-spin" />
          : <Search  className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
        }
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value.toUpperCase())}
          placeholder="search ticker"
          disabled={loading}
          className="w-full bg-gray-900 border border-gray-700 rounded-xl pl-12 pr-36 py-4
                     text-white placeholder-gray-500 text-lg
                     focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500
                     disabled:opacity-60 disabled:cursor-not-allowed
                     transition-colors"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="absolute right-3 top-1/2 -translate-y-1/2
                     bg-violet-600 hover:bg-violet-500 disabled:bg-violet-900
                     disabled:cursor-not-allowed text-white
                     px-4 py-2 rounded-lg text-sm font-medium transition-colors
                     flex items-center gap-2 min-w-22.5 justify-center"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Loading...
            </>
          ) : "Search"}
        </button>
      </form>

      {loading && (
        <p className="text-center text-sm text-violet-400 mt-3 animate-pulse">
          Fetching data for {query}
        </p>
      )}

      {!loading && (
        <div className="flex gap-2 mt-3 flex-wrap justify-center">
          {POPULAR.map((t) => (
            <button
              key={t}
              onClick={() => navigate(t)}
              className="px-3 py-1 text-xs bg-gray-800 hover:bg-gray-700
                         text-gray-400 hover:text-white rounded-full transition-colors"
            >
              {t}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}