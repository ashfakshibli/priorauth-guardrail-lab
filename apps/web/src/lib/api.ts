import type {
  CaseListItem,
  CaseDetail,
  PolicyContext,
  DecisionRun,
  Trace,
  EvalResult,
  ReviewQueueItem,
} from "@/types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${path} → ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  cases: {
    list: () => apiFetch<CaseListItem[]>("/api/cases"),
    get: (id: string) => apiFetch<CaseDetail>(`/api/cases/${id}`),
    policyContext: (id: string) => apiFetch<PolicyContext>(`/api/cases/${id}/policy-context`),
    runDecision: (id: string) =>
      apiFetch<DecisionRun>(`/api/cases/${id}/run-decision`, { method: "POST" }),
  },
  runs: {
    get: (id: string) => apiFetch<DecisionRun>(`/api/runs/${id}`),
    trace: (id: string) => apiFetch<Trace>(`/api/runs/${id}/trace`),
    evals: (id: string) => apiFetch<EvalResult>(`/api/runs/${id}/evals`),
  },
  queue: {
    list: () => apiFetch<ReviewQueueItem[]>("/api/review-queue"),
  },
};
