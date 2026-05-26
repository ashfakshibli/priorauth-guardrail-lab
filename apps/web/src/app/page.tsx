import Link from "next/link";
import { api } from "@/lib/api";
import type { CaseListItem, CaseStatus } from "@/types";

export const dynamic = "force-dynamic";

const serviceLabel: Record<string, string> = {
  J0885: "Adalimumab (Biologic)",
  J1745: "Infliximab (Biologic)",
  "72148": "MRI Lumbar Spine",
  "78816": "PET Scan – Whole Body",
  H0018: "Residential BH",
  "29881": "Knee Arthroscopy",
  "99999": "Unlisted / Experimental",
};

const statusConfig: Record<CaseStatus, { label: string; dot: string; badge: string }> = {
  pending:      { label: "Pending",      dot: "bg-slate-400",  badge: "bg-slate-100 text-slate-600" },
  approved:     { label: "Approved",     dot: "bg-emerald-500",badge: "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200" },
  denied:       { label: "Denied",       dot: "bg-red-500",    badge: "bg-red-50 text-red-700 ring-1 ring-red-200" },
  under_review: { label: "In Review",    dot: "bg-amber-500",  badge: "bg-amber-50 text-amber-700 ring-1 ring-amber-200" },
};

function StatusBadge({ status }: { status: CaseStatus }) {
  const cfg = statusConfig[status] ?? statusConfig.pending;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${cfg.badge}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${cfg.dot}`} />
      {cfg.label}
    </span>
  );
}

function StatCard({ label, value, sub }: { label: string; value: number; sub?: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-bold text-slate-900 tabular-nums">{value}</p>
      {sub && <p className="mt-0.5 text-xs text-slate-400">{sub}</p>}
    </div>
  );
}

export default async function CasesPage() {
  let cases: CaseListItem[] = [];
  let error: string | null = null;
  try {
    cases = await api.cases.list();
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed to load cases";
  }

  const stats = {
    total: cases.length,
    pending: cases.filter(c => c.status === "pending").length,
    approved: cases.filter(c => c.status === "approved").length,
    denied: cases.filter(c => c.status === "denied").length,
    review: cases.filter(c => c.status === "under_review").length,
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page header */}
      <div className="border-b border-slate-200 bg-white px-8 py-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-slate-900">Authorization Cases</h1>
            <p className="mt-0.5 text-sm text-slate-500">
              Synthetic demo queue · deterministic rules engine + guardrail validation
            </p>
          </div>
          <span className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-600 ring-1 ring-indigo-200">
            DEMO
          </span>
        </div>
      </div>

      <div className="px-8 py-6 max-w-7xl mx-auto space-y-6">
        {/* Stats */}
        <div className="grid grid-cols-5 gap-4">
          <StatCard label="Total Cases" value={stats.total} />
          <StatCard label="Pending"     value={stats.pending}   sub="awaiting decision" />
          <StatCard label="Approved"    value={stats.approved}  sub="coverage confirmed" />
          <StatCard label="Denied"      value={stats.denied}    sub="not covered" />
          <StatCard label="In Review"   value={stats.review}    sub="human escalation" />
        </div>

        {error && (
          <div className="flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            <svg className="h-4 w-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            {error} — is the API running at{" "}
            <code className="font-mono text-xs bg-red-100 px-1 rounded">{process.env.NEXT_PUBLIC_API_URL}</code>?
          </div>
        )}

        {/* Table */}
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/70">
                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">Case</th>
                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">Member</th>
                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">Service</th>
                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">Age Band</th>
                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">Status</th>
                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">Tags</th>
                <th className="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {cases.map((c) => (
                <tr key={c.id} className="group hover:bg-indigo-50/30 transition-colors">
                  <td className="px-5 py-4">
                    <span className="font-mono text-xs font-semibold text-indigo-600">{c.id}</span>
                  </td>
                  <td className="px-5 py-4">
                    <div className="font-semibold text-slate-800">{c.member_id}</div>
                    <div className="text-xs text-slate-400">{c.provider_id}</div>
                  </td>
                  <td className="px-5 py-4">
                    <div className="font-medium text-slate-800 max-w-[200px] truncate">
                      {serviceLabel[c.service_code] ?? c.service_description}
                    </div>
                    <div className="font-mono text-xs text-slate-400 mt-0.5">{c.service_code}</div>
                  </td>
                  <td className="px-5 py-4">
                    <span className="rounded-md bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                      {c.age_band}
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    <StatusBadge status={c.status} />
                  </td>
                  <td className="px-5 py-4">
                    <div className="flex flex-wrap gap-1">
                      {(c.tags ?? []).slice(0, 2).map((t) => (
                        <span key={t} className="rounded-md bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-500">
                          {t}
                        </span>
                      ))}
                      {(c.tags ?? []).length > 2 && (
                        <span className="text-[10px] text-slate-400">+{c.tags.length - 2}</span>
                      )}
                    </div>
                  </td>
                  <td className="px-5 py-4 text-right">
                    <Link
                      href={`/cases/${c.id}`}
                      className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-700 transition-colors group-hover:shadow-md"
                    >
                      Review
                      <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                      </svg>
                    </Link>
                  </td>
                </tr>
              ))}
              {cases.length === 0 && !error && (
                <tr>
                  <td colSpan={7} className="px-5 py-16 text-center text-slate-400">
                    No cases found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
