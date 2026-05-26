import Link from "next/link";
import { api } from "@/lib/api";
import type { ReviewQueueItem } from "@/types";

export const dynamic = "force-dynamic";

const priorityConfig = {
  high:   { label: "High",   dot: "bg-red-500",    badge: "bg-red-50 text-red-700 ring-1 ring-red-200",   bar: "bg-red-400" },
  medium: { label: "Medium", dot: "bg-amber-500",  badge: "bg-amber-50 text-amber-700 ring-1 ring-amber-200", bar: "bg-amber-400" },
  low:    { label: "Low",    dot: "bg-slate-400",  badge: "bg-slate-100 text-slate-600",                   bar: "bg-slate-300" },
};

function PriorityBadge({ priority }: { priority: string }) {
  const cfg = priorityConfig[priority as keyof typeof priorityConfig] ?? priorityConfig.low;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${cfg.badge}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${cfg.dot}`} />
      {cfg.label}
    </span>
  );
}

function QueueCard({ item }: { item: ReviewQueueItem }) {
  const cfg = priorityConfig[item.priority as keyof typeof priorityConfig] ?? priorityConfig.low;
  const createdAt = new Date(item.created_at);
  const now = new Date();
  const diffMs = now.getTime() - createdAt.getTime();
  const diffHrs = Math.floor(diffMs / 3600000);
  const diffMins = Math.floor((diffMs % 3600000) / 60000);
  const age = diffHrs > 0 ? `${diffHrs}h ${diffMins}m ago` : `${diffMins}m ago`;

  return (
    <div className="group relative overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm hover:border-indigo-200 hover:shadow-md transition-all">
      <div className={`absolute left-0 top-0 h-full w-1 ${cfg.bar}`} />
      <div className="pl-5 pr-5 py-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2.5 mb-1.5">
              <span className="font-mono text-sm font-bold text-indigo-600">{item.case_id}</span>
              <PriorityBadge priority={item.priority} />
            </div>
            <p className="text-sm text-slate-700 leading-relaxed line-clamp-2">{item.reason}</p>
          </div>
          <Link
            href={`/cases/${item.case_id}`}
            className="flex-shrink-0 inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-700 transition-colors group-hover:shadow-md"
          >
            Review
            <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </Link>
        </div>
        <div className="mt-3 flex items-center gap-4 text-[10px] text-slate-400">
          <span className="flex items-center gap-1">
            <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {age}
          </span>
          <span className="flex items-center gap-1 font-mono">
            <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 8.25h15m-16.5 7.5h15m-1.8-13.5l-3.9 19.5m-2.1-19.5l-3.9 19.5" />
            </svg>
            {item.run_id.slice(0, 12)}…
          </span>
        </div>
      </div>
    </div>
  );
}

export default async function ReviewQueuePage() {
  let items: ReviewQueueItem[] = [];
  let error: string | null = null;

  try {
    items = await api.queue.list();
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed to load queue";
  }

  const high = items.filter(i => i.priority === "high");
  const medium = items.filter(i => i.priority === "medium");
  const low = items.filter(i => i.priority === "low");

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page header */}
      <div className="border-b border-slate-200 bg-white px-8 py-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-slate-900">Review Queue</h1>
            <p className="mt-0.5 text-sm text-slate-500">
              Cases escalated for human review — low confidence, guardrail failures, or conflicting policy signals
            </p>
          </div>
          {items.length > 0 && (
            <div className="flex items-center gap-3">
              {high.length > 0 && (
                <span className="flex items-center gap-1.5 rounded-full bg-red-50 px-3 py-1 text-xs font-semibold text-red-700 ring-1 ring-red-200">
                  <span className="h-1.5 w-1.5 rounded-full bg-red-500" />
                  {high.length} High
                </span>
              )}
              {medium.length > 0 && (
                <span className="flex items-center gap-1.5 rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700 ring-1 ring-amber-200">
                  <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                  {medium.length} Medium
                </span>
              )}
              {low.length > 0 && (
                <span className="flex items-center gap-1.5 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                  <span className="h-1.5 w-1.5 rounded-full bg-slate-400" />
                  {low.length} Low
                </span>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="px-8 py-6 max-w-4xl mx-auto">
        {error && (
          <div className="mb-5 flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            <svg className="h-4 w-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            {error}
          </div>
        )}

        {items.length === 0 && !error ? (
          <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 bg-white py-20">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-100">
              <svg className="h-6 w-6 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
              </svg>
            </div>
            <p className="mt-4 text-sm font-medium text-slate-600">Queue is clear</p>
            <p className="mt-1 text-xs text-slate-400">Run decisions on cases to populate this view</p>
          </div>
        ) : (
          <div className="space-y-3">
            {items.map((item) => (
              <QueueCard key={item.id} item={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
