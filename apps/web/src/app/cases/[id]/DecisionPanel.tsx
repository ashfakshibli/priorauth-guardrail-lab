"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { DecisionRun, Trace, EvalResult } from "@/types";

interface Props { caseId: string }
type Tab = "decision" | "trace" | "evals";

// ── Determination hero ────────────────────────────────────────────────────────

const detConfig = {
  approve: {
    bg: "bg-emerald-600",
    light: "bg-emerald-50 border-emerald-200",
    text: "text-emerald-700",
    label: "APPROVED",
    icon: (
      <svg className="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  deny: {
    bg: "bg-red-600",
    light: "bg-red-50 border-red-200",
    text: "text-red-700",
    label: "DENIED",
    icon: (
      <svg className="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  human_review: {
    bg: "bg-amber-500",
    light: "bg-amber-50 border-amber-200",
    text: "text-amber-700",
    label: "HUMAN REVIEW",
    icon: (
      <svg className="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
      </svg>
    ),
  },
};

function DeterminationHero({ run }: { run: DecisionRun }) {
  const cfg = detConfig[run.determination];
  const pct = Math.round(run.confidence_score * 100);
  const confColor = pct >= 75 ? "bg-emerald-500" : pct >= 55 ? "bg-amber-400" : "bg-red-500";
  const confLabel = pct >= 75 ? "High" : pct >= 55 ? "Moderate" : "Low";

  return (
    <div className={`rounded-xl border ${cfg.light} overflow-hidden`}>
      {/* Banner */}
      <div className={`${cfg.bg} px-5 py-4 flex items-center gap-3`}>
        {cfg.icon}
        <div>
          <p className="text-xs font-semibold text-white/70 uppercase tracking-widest">Determination</p>
          <p className="text-xl font-bold text-white tracking-wide">{cfg.label}</p>
        </div>
        <div className="ml-auto text-right">
          <p className="text-xs text-white/70 uppercase tracking-widest">Latency</p>
          <p className="text-sm font-semibold text-white">{run.latency_ms}ms</p>
        </div>
      </div>

      {/* Confidence */}
      <div className="px-5 py-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">Confidence</span>
          <div className="flex items-center gap-2">
            <span className={`text-xs font-semibold ${cfg.text}`}>{confLabel}</span>
            <span className="text-sm font-bold text-slate-800 tabular-nums">{pct}%</span>
          </div>
        </div>
        <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
          <div
            className={`h-full rounded-full ${confColor} transition-all duration-700`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <div className="mt-1 flex justify-between text-[10px] text-slate-300">
          <span>0</span><span>55</span><span>75</span><span>100</span>
        </div>
      </div>
    </div>
  );
}

// ── Guardrail section ─────────────────────────────────────────────────────────

const grConfig = {
  pass:    { bg: "bg-emerald-50", border: "border-emerald-200", icon: "✓", iconColor: "text-emerald-600", label: "All checks passed", labelColor: "text-emerald-700" },
  warning: { bg: "bg-amber-50",   border: "border-amber-200",   icon: "⚠", iconColor: "text-amber-600",  label: "Warnings detected",  labelColor: "text-amber-700" },
  fail:    { bg: "bg-red-50",     border: "border-red-200",     icon: "✕", iconColor: "text-red-600",    label: "Guardrail failed",   labelColor: "text-red-700" },
};

function GuardrailSection({ run }: { run: DecisionRun }) {
  const cfg = grConfig[run.guardrail_status as keyof typeof grConfig] ?? grConfig.pass;
  return (
    <div className={`rounded-xl border ${cfg.border} ${cfg.bg} px-4 py-3`}>
      <div className="flex items-center gap-2 mb-2">
        <span className={`text-base font-bold ${cfg.iconColor}`}>{cfg.icon}</span>
        <span className={`text-xs font-semibold uppercase tracking-wide ${cfg.labelColor}`}>
          Guardrail · {cfg.label}
        </span>
      </div>
      {run.guardrail_reasons.length === 0 ? (
        <p className="text-xs text-slate-500">No issues detected by the validator.</p>
      ) : (
        <ul className="space-y-1">
          {run.guardrail_reasons.map((r, i) => (
            <li key={i} className="text-xs text-slate-600 flex gap-2">
              <span className="mt-0.5 flex-shrink-0 font-mono text-[10px] text-slate-400">
                {r.match(/GR-\d/)?.[0] ?? "·"}
              </span>
              <span>{r.replace(/^GR-\d+:\s*/, "")}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ── Citations ─────────────────────────────────────────────────────────────────

function Citations({ run }: { run: DecisionRun }) {
  if (!run.policy_citations.length) return null;
  return (
    <div>
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
        Policy Citations · {run.policy_citations.length}
      </p>
      <div className="space-y-2">
        {run.policy_citations.map((c) => (
          <div key={c.clause_id} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
            <div className="flex items-start justify-between gap-2">
              <span className="font-mono text-[11px] font-semibold text-indigo-600">{c.clause_id}</span>
              <div className="flex items-center gap-1">
                <div className="flex gap-0.5">
                  {[1,2,3,4,5].map(n => (
                    <span key={n} className={`h-1.5 w-2.5 rounded-sm ${n <= Math.ceil(Math.min(c.relevance_score, 15) / 3) ? "bg-indigo-500" : "bg-slate-200"}`} />
                  ))}
                </div>
                <span className="text-[9px] text-slate-400">{c.relevance_score}</span>
              </div>
            </div>
            <p className="mt-0.5 text-xs text-slate-600">{c.section}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Trace ─────────────────────────────────────────────────────────────────────

const stepIcons: Record<string, string> = {
  load_case:          "📋",
  retrieve_clauses:   "🔍",
  rules_engine:       "⚙️",
  llm_enhancement:    "✨",
  guardrail_validator:"🛡️",
  eval_scoring:       "📊",
};

function TraceStepRow({ event, idx, total }: { event: Trace["events"][0]; idx: number; total: number }) {
  const [open, setOpen] = useState(false);
  const durationMs = new Date(event.ended_at).getTime() - new Date(event.started_at).getTime();
  const isOk = event.status === "ok";
  const isError = event.status.startsWith("error");
  const isSkipped = event.status.includes("skipped");

  const dotColor = isOk ? "bg-emerald-500" : isError ? "bg-red-500" : isSkipped ? "bg-slate-300" : "bg-amber-400";
  const lineColor = isOk ? "bg-emerald-200" : isError ? "bg-red-200" : "bg-slate-200";

  return (
    <div className="flex gap-3">
      {/* Timeline column */}
      <div className="flex flex-col items-center">
        <div className={`h-2.5 w-2.5 flex-shrink-0 rounded-full mt-3.5 ${dotColor} ring-2 ring-white`} />
        {idx < total - 1 && <div className={`w-0.5 flex-1 mt-1 ${lineColor}`} />}
      </div>

      {/* Content */}
      <div className="flex-1 pb-3">
        <button
          onClick={() => setOpen(p => !p)}
          className="flex w-full items-center gap-2 text-left"
        >
          <span className="text-sm">{stepIcons[event.step_name] ?? "•"}</span>
          <span className="flex-1 font-mono text-[12px] font-semibold text-slate-700">{event.step_name}</span>
          <span className="text-[10px] text-slate-400 tabular-nums">{durationMs}ms</span>
          <span className="text-slate-300 text-xs ml-1">{open ? "▴" : "▾"}</span>
        </button>

        {event.warning_flags.length > 0 && (
          <p className="mt-1 text-[11px] text-amber-600 flex items-center gap-1">
            <span>⚠</span>
            {event.warning_flags[0].replace(/^GR-\d+:\s*/, "").slice(0, 70)}
            {event.warning_flags[0].length > 70 ? "…" : ""}
          </p>
        )}

        {open && (
          <div className="mt-2 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2.5 space-y-1.5 text-[11px]">
            <div><span className="text-slate-400 font-semibold">IN: </span><span className="text-slate-600">{event.input_summary}</span></div>
            <div><span className="text-slate-400 font-semibold">OUT: </span><span className="text-slate-600">{event.output_summary}</span></div>
            {event.artifact_refs.length > 0 && (
              <div>
                <span className="text-slate-400 font-semibold">REFS: </span>
                <span className="font-mono text-indigo-600">{event.artifact_refs.join(", ")}</span>
              </div>
            )}
            {event.warning_flags.map((w, i) => (
              <div key={i} className="rounded bg-amber-50 border border-amber-100 px-2 py-1 text-amber-700">⚠ {w}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Evals ─────────────────────────────────────────────────────────────────────

function EvalRow({ label, value, invert = false, desc }: { label: string; value: boolean | number; invert?: boolean; desc?: string }) {
  let indicator: React.ReactNode;
  let positive: boolean;

  if (typeof value === "boolean") {
    positive = invert ? !value : value;
    indicator = (
      <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${positive ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}`}>
        {positive ? "✓" : "✕"} {value ? "Yes" : "No"}
      </span>
    );
  } else {
    const pct = Math.round(value * 100);
    positive = pct >= 50;
    indicator = (
      <div className="flex items-center gap-2">
        <div className="w-24 h-1.5 rounded-full bg-slate-100 overflow-hidden">
          <div
            className={`h-full rounded-full ${pct >= 75 ? "bg-emerald-500" : pct >= 50 ? "bg-amber-400" : "bg-red-500"}`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <span className={`text-xs font-bold tabular-nums ${pct >= 75 ? "text-emerald-600" : pct >= 50 ? "text-amber-600" : "text-red-600"}`}>{pct}%</span>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between py-2.5 border-b border-slate-50 last:border-0">
      <div>
        <p className="text-sm text-slate-700">{label}</p>
        {desc && <p className="text-[10px] text-slate-400">{desc}</p>}
      </div>
      {indicator}
    </div>
  );
}

// ── Main panel ────────────────────────────────────────────────────────────────

export function DecisionPanel({ caseId }: Props) {
  const [tab, setTab] = useState<Tab>("decision");
  const [run, setRun] = useState<DecisionRun | null>(null);
  const [trace, setTrace] = useState<Trace | null>(null);
  const [evals, setEvals] = useState<EvalResult | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function executeRun() {
    setRunning(true);
    setError(null);
    try {
      const r = await api.cases.runDecision(caseId);
      setRun(r);
      const [t, e] = await Promise.all([api.runs.trace(r.run_id), api.runs.evals(r.run_id)]);
      setTrace(t);
      setEvals(e);
      setTab("decision");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Decision run failed");
    } finally {
      setRunning(false);
    }
  }

  const tabs: { key: Tab; label: string; count?: number }[] = [
    { key: "decision", label: "Decision" },
    { key: "trace",    label: "Trace",  count: trace?.events.length },
    { key: "evals",    label: "Evals" },
  ];

  return (
    <div className="space-y-3" id="decision">
      {/* Run button */}
      <button
        onClick={executeRun}
        disabled={running}
        className="flex w-full items-center justify-center gap-2.5 rounded-xl bg-indigo-600 px-5 py-3.5 text-sm font-semibold text-white shadow-md hover:bg-indigo-700 active:scale-[0.99] disabled:opacity-60 transition-all"
      >
        {running ? (
          <>
            <span className="h-4 w-4 animate-spin rounded-full border-[2.5px] border-white border-t-transparent" />
            Running pipeline…
          </>
        ) : (
          <>
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
            </svg>
            {run ? "Re-run Decision Engine" : "Run Decision Engine"}
          </>
        )}
      </button>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Results card */}
      {run && (
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          {/* Tabs */}
          <div className="flex border-b border-slate-100 bg-slate-50/50">
            {tabs.map(({ key, label, count }) => (
              <button
                key={key}
                onClick={() => setTab(key)}
                className={`flex flex-1 items-center justify-center gap-1.5 py-2.5 text-xs font-semibold transition-colors ${
                  tab === key
                    ? "border-b-2 border-indigo-600 text-indigo-700 bg-white"
                    : "text-slate-400 hover:text-slate-600"
                }`}
              >
                {label}
                {count !== undefined && (
                  <span className={`rounded-full px-1.5 py-0.5 text-[9px] font-bold ${tab === key ? "bg-indigo-100 text-indigo-600" : "bg-slate-200 text-slate-500"}`}>
                    {count}
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Decision tab */}
          {tab === "decision" && (
            <div className="p-4 space-y-4">
              <DeterminationHero run={run} />
              <GuardrailSection run={run} />

              {/* Rationale */}
              <div>
                <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Rationale
                  {run.llm_enhanced && (
                    <span className="ml-2 inline-flex items-center gap-1 rounded-full bg-purple-100 px-1.5 py-0.5 text-[9px] font-bold text-purple-600">
                      ✨ LLM enhanced
                    </span>
                  )}
                </p>
                <p className="text-[13px] text-slate-600 leading-relaxed rounded-lg bg-slate-50 border border-slate-100 px-3 py-3">
                  {run.rationale_summary}
                </p>
              </div>

              <Citations run={run} />

              <p className="font-mono text-[9px] text-slate-300 text-right">
                run: {run.run_id.slice(0, 16)}…
              </p>
            </div>
          )}

          {/* Trace tab */}
          {tab === "trace" && trace && (
            <div className="px-4 py-4">
              <div className="flex items-center justify-between mb-4">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Execution trace</p>
                <span className="text-[10px] text-slate-400 font-mono">{trace.events.length} steps</span>
              </div>
              {trace.events.map((evt, i) => (
                <TraceStepRow key={evt.id} event={evt} idx={i} total={trace.events.length} />
              ))}
            </div>
          )}

          {/* Evals tab */}
          {tab === "evals" && evals && (
            <div className="p-4 space-y-3">
              {/* Overall badge */}
              <div className={`flex items-center justify-between rounded-xl px-4 py-3 border ${
                evals.overall_eval_status === "pass" ? "bg-emerald-50 border-emerald-200" :
                evals.overall_eval_status === "warning" ? "bg-amber-50 border-amber-200" :
                "bg-red-50 border-red-200"
              }`}>
                <p className="text-sm font-semibold text-slate-700">Overall eval status</p>
                <span className={`text-sm font-bold uppercase tracking-wide ${
                  evals.overall_eval_status === "pass" ? "text-emerald-700" :
                  evals.overall_eval_status === "warning" ? "text-amber-700" : "text-red-700"
                }`}>
                  {evals.overall_eval_status === "pass" ? "✓ Pass" : evals.overall_eval_status === "warning" ? "⚠ Warning" : "✕ Fail"}
                </span>
              </div>

              <div className="divide-y divide-slate-50">
                <EvalRow label="Policy Coverage" value={evals.policy_coverage_score} desc="fraction of required clauses retrieved" />
                <EvalRow label="Citation Presence" value={evals.citation_presence} desc="at least one clause cited" />
                <EvalRow label="Contradiction Detected" value={evals.contradiction_flag} invert desc="conflicting approve/deny hints" />
                <EvalRow label="Missing Evidence" value={evals.missing_evidence_flag} invert desc="no supporting clauses found" />
                <EvalRow label="Escalation Correct" value={evals.escalation_correctness} desc="routing matched confidence level" />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {!run && !running && (
        <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 py-12 text-center">
          <div className="h-10 w-10 rounded-full bg-slate-100 flex items-center justify-center mb-3">
            <svg className="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
            </svg>
          </div>
          <p className="text-sm font-semibold text-slate-500">No decision run yet</p>
          <p className="text-xs text-slate-400 mt-1">Click Run Decision Engine to start</p>
        </div>
      )}
    </div>
  );
}
