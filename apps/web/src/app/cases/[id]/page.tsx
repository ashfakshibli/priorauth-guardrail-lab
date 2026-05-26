import { notFound } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { DecisionPanel } from "./DecisionPanel";

export const dynamic = "force-dynamic";

interface Props {
  params: Promise<{ id: string }>;
}

const statusConfig: Record<string, { label: string; dot: string; badge: string }> = {
  pending:      { label: "Pending",   dot: "bg-slate-400",   badge: "bg-slate-100 text-slate-600" },
  approved:     { label: "Approved",  dot: "bg-emerald-500", badge: "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200" },
  denied:       { label: "Denied",    dot: "bg-red-500",     badge: "bg-red-50 text-red-700 ring-1 ring-red-200" },
  under_review: { label: "In Review", dot: "bg-amber-500",   badge: "bg-amber-50 text-amber-700 ring-1 ring-amber-200" },
};

function StatusBadge({ status }: { status: string }) {
  const cfg = statusConfig[status] ?? statusConfig.pending;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${cfg.badge}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${cfg.dot}`} />
      {cfg.label}
    </span>
  );
}

function SectionCard({
  title,
  icon,
  children,
}: {
  title: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center gap-2 border-b border-slate-100 bg-slate-50/60 px-5 py-3">
        {icon && <span className="text-slate-400">{icon}</span>}
        <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</h2>
      </div>
      {children}
    </div>
  );
}

export default async function CaseDetailPage({ params }: Props) {
  const { id } = await params;

  let caseData;
  let policyContext;
  try {
    [caseData, policyContext] = await Promise.all([
      api.cases.get(id),
      api.cases.policyContext(id),
    ]);
  } catch {
    notFound();
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page header */}
      <div className="border-b border-slate-200 bg-white px-8 py-5">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-2 text-xs text-slate-400 mb-3">
            <Link href="/" className="hover:text-indigo-600 transition-colors font-medium">
              Cases
            </Link>
            <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
            <span className="font-mono font-semibold text-slate-600">{id}</span>
          </div>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-xl font-semibold text-slate-900">{caseData.service_description}</h1>
              <p className="mt-0.5 font-mono text-sm text-slate-400">{caseData.service_code}</p>
            </div>
            <StatusBadge status={caseData.status} />
          </div>
        </div>
      </div>

      <div className="px-8 py-6 max-w-7xl mx-auto">
        <div className="grid grid-cols-3 gap-6">
          {/* Left: Case Details */}
          <div className="col-span-2 space-y-5">
            {/* Case Summary */}
            <SectionCard
              title="Case Summary"
              icon={
                <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
                </svg>
              }
            >
              <div className="px-5 py-4">
                <dl className="grid grid-cols-2 gap-x-8 gap-y-4 text-sm">
                  <div>
                    <dt className="text-[10px] font-semibold uppercase tracking-widest text-slate-400">Member</dt>
                    <dd className="mt-1 font-mono font-semibold text-slate-800">{caseData.member_id}</dd>
                  </div>
                  <div>
                    <dt className="text-[10px] font-semibold uppercase tracking-widest text-slate-400">Provider</dt>
                    <dd className="mt-1 font-mono font-semibold text-slate-800">{caseData.provider_id}</dd>
                  </div>
                  <div>
                    <dt className="text-[10px] font-semibold uppercase tracking-widest text-slate-400">Age Band</dt>
                    <dd className="mt-1">
                      <span className="rounded-md bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
                        {caseData.age_band}
                      </span>
                    </dd>
                  </div>
                  <div>
                    <dt className="text-[10px] font-semibold uppercase tracking-widest text-slate-400">Service Code</dt>
                    <dd className="mt-1 font-mono text-sm font-semibold text-indigo-600">{caseData.service_code}</dd>
                  </div>
                  {caseData.tags && caseData.tags.length > 0 && (
                    <div className="col-span-2">
                      <dt className="text-[10px] font-semibold uppercase tracking-widest text-slate-400">Tags</dt>
                      <dd className="mt-1.5 flex flex-wrap gap-1.5">
                        {caseData.tags.map((t: string) => (
                          <span key={t} className="rounded-md bg-indigo-50 px-2 py-0.5 text-[10px] font-semibold text-indigo-600">
                            {t}
                          </span>
                        ))}
                      </dd>
                    </div>
                  )}
                  <div className="col-span-2">
                    <dt className="text-[10px] font-semibold uppercase tracking-widest text-slate-400">Diagnosis Codes</dt>
                    <dd className="mt-1.5 flex flex-wrap gap-1.5">
                      {caseData.diagnosis_codes.length > 0 ? (
                        caseData.diagnosis_codes.map((dx: string) => (
                          <span key={dx} className="rounded-md bg-slate-100 px-2 py-0.5 font-mono text-xs font-medium text-slate-600">
                            {dx}
                          </span>
                        ))
                      ) : (
                        <span className="text-sm italic text-slate-400">None provided</span>
                      )}
                    </dd>
                  </div>
                </dl>
              </div>
            </SectionCard>

            {/* Clinical Notes */}
            <SectionCard
              title="Clinical Notes"
              icon={
                <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                </svg>
              }
            >
              <div className="px-5 py-4">
                {caseData.clinical_notes_summary ? (
                  <p className="text-sm text-slate-700 leading-relaxed">{caseData.clinical_notes_summary}</p>
                ) : (
                  <div className="flex items-center gap-2 text-sm text-slate-400">
                    <svg className="h-4 w-4 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                    </svg>
                    <span className="italic">No clinical notes attached — may trigger GR-4 guardrail.</span>
                  </div>
                )}
              </div>
            </SectionCard>

            {/* Policy Pack */}
            <SectionCard
              title={`Policy Pack · ${policyContext.policy_documents.length} document${policyContext.policy_documents.length !== 1 ? "s" : ""}`}
              icon={
                <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                </svg>
              }
            >
              {policyContext.policy_documents.length === 0 ? (
                <div className="px-5 py-4 text-sm italic text-slate-400">No policy documents attached.</div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {policyContext.policy_documents.map((doc: {
                    id: string; title: string; payer_code: string; effective_date: string;
                    clauses: Array<{ id: string; section: string; clause_text: string; determination_hint: string | null; tags: string[] }>;
                  }) => (
                    <div key={doc.id} className="px-5 py-4">
                      <div className="mb-3 flex items-center justify-between">
                        <div>
                          <div className="font-semibold text-slate-800 text-sm">{doc.title}</div>
                          <div className="mt-0.5 flex items-center gap-2 font-mono text-[10px] text-slate-400">
                            <span>{doc.id}</span>
                            <span>·</span>
                            <span>{doc.payer_code}</span>
                            <span>·</span>
                            <span>Effective {doc.effective_date}</span>
                          </div>
                        </div>
                        <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-500">
                          {doc.clauses.length} clause{doc.clauses.length !== 1 ? "s" : ""}
                        </span>
                      </div>
                      <div className="space-y-2">
                        {doc.clauses.map((clause) => (
                          <div
                            key={clause.id}
                            className={`rounded-lg border px-3 py-2.5 ${
                              clause.determination_hint === "approve"
                                ? "border-emerald-100 bg-emerald-50/40"
                                : clause.determination_hint === "deny"
                                ? "border-red-100 bg-red-50/40"
                                : clause.determination_hint === "human_review"
                                ? "border-amber-100 bg-amber-50/40"
                                : "border-slate-100 bg-slate-50"
                            }`}
                          >
                            <div className="flex items-center justify-between mb-1.5">
                              <span className="font-mono text-[11px] font-bold text-indigo-600">{clause.id}</span>
                              {clause.determination_hint && (
                                <span
                                  className={`text-[10px] font-bold uppercase tracking-wide px-2 py-0.5 rounded-full ${
                                    clause.determination_hint === "approve"
                                      ? "bg-emerald-100 text-emerald-700"
                                      : clause.determination_hint === "deny"
                                      ? "bg-red-100 text-red-700"
                                      : "bg-amber-100 text-amber-700"
                                  }`}
                                >
                                  {clause.determination_hint.replace("_", " ")}
                                </span>
                              )}
                            </div>
                            <div className="text-[10px] font-semibold uppercase tracking-wide text-slate-400 mb-1">
                              {clause.section}
                            </div>
                            <p className="text-xs text-slate-600 leading-relaxed">{clause.clause_text}</p>
                            {clause.tags.length > 0 && (
                              <div className="mt-2 flex flex-wrap gap-1">
                                {clause.tags.map((t) => (
                                  <span
                                    key={t}
                                    className="rounded bg-white/70 border border-slate-200 px-1.5 py-0.5 text-[9px] font-medium text-slate-400"
                                  >
                                    {t}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </SectionCard>
          </div>

          {/* Right: Decision Panel */}
          <div className="col-span-1">
            <div className="sticky top-6">
              <div className="mb-3 flex items-center gap-2">
                <div className="h-5 w-1 rounded-full bg-indigo-500" />
                <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Decision Engine</h2>
              </div>
              <DecisionPanel caseId={id} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
