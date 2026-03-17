"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";

const POPULAR = ["NVDA", "AAPL", "TSLA", "MSFT", "AMZN", "GOOGL", "META"];

export default function SearchBar() {
  const [query, setQuery]   = useState("");
  const router              = useRouter();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const ticker = query.trim().toUpperCase();
    if (ticker) router.push(`/company/${ticker}`);
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value.toUpperCase())}
          placeholder="Search ticker — NVDA, AAPL, TSLA..."
          className="w-full bg-gray-900 border border-gray-700 rounded-xl pl-12 pr-4 py-4
                     text-white placeholder-gray-500 text-lg
                     focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500
                     transition-colors"
        />
        <button
          type="submit"
          className="absolute right-3 top-1/2 -translate-y-1/2
                     bg-violet-600 hover:bg-violet-500 text-white
                     px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          Search
        </button>
      </form>

      <div className="flex gap-2 mt-3 flex-wrap justify-center">
        {POPULAR.map((t) => (
          <button
            key={t}
            onClick={() => router.push(`/company/${t}`)}
            className="px-3 py-1 text-xs bg-gray-800 hover:bg-gray-700
                       text-gray-400 hover:text-white rounded-full transition-colors"
          >
            {t}
          </button>
        ))}
      </div>
    </div>
  );
}