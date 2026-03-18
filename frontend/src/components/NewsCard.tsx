import { clsx } from "clsx";
import type { NewsArticle } from "@/lib/api";

interface Props {
  articles: NewsArticle[];
}

function SentimentBadge({ label }: { label: string | null }) {
  if (!label) return null;

  return (
    <span
      className={clsx(
        "text-xs px-2 py-0.5 rounded-full font-medium shrink-0",
        label === "positive" && "bg-emerald-900/50 text-emerald-400",
        label === "negative" && "bg-red-900/50 text-red-400",
        label === "neutral" && "bg-gray-800 text-gray-400"
      )}
    >
      {label}
    </span>
  );
}

export default function NewsCard({ articles }: Props) {
  if (!articles || articles.length === 0) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 text-gray-500 text-sm">
        No recent news found.
      </div>
    );
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-1">
      <h3 className="font-semibold text-white mb-3">Recent news</h3>

      {articles.map((article, i) => (
        <div
          key={article.url || `${article.title}-${i}`}
          className="py-3 border-b border-gray-800 last:border-0 space-y-1"
        >
          <div className="flex items-start justify-between gap-3">
            {article.url ? (
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-gray-200 leading-snug hover:text-violet-400 transition-colors cursor-pointer"
              >
                {article.title}
              </a>
            ) : (
              <p className="text-sm text-gray-200 leading-snug">
                {article.title}
              </p>
            )}

            <SentimentBadge label={article.sentiment_label} />
          </div>

          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span>{article.source}</span>
            <span>·</span>

            <span>
              {new Date(article.published_at).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>

            {article.sentiment_compound !== null && (
              <>
                <span>·</span>
                <span
                  className={clsx(
                    "font-mono",
                    (article.sentiment_compound ?? 0) > 0 && "text-emerald-500",
                    (article.sentiment_compound ?? 0) < 0 && "text-red-500",
                    (article.sentiment_compound ?? 0) === 0 && "text-gray-500"
                  )}
                >
                  {(article.sentiment_compound ?? 0).toFixed(3)}
                </span>
              </>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
