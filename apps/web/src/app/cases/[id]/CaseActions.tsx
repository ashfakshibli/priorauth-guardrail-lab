"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { DecisionRun } from "@/types";

interface Props {
  caseId: string;
}

export function CaseActions({ caseId }: Props) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DecisionRun | null>(null);

  async function handleRun() {
    setLoading(true);
    setError(null);
    try {
      const run = await api.cases.runDecision(caseId);
      setResult(run);
      router.refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Decision run failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-3">
      <button
        onClick={handleRun}
        disabled={loading}
        className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-60 transition-colors"
      >
        {loading ? (
          <>
            <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white border-t-transparent" />
            Running decision…
          </>
        ) : (
          "Run Decision Engine"
        )}
      </button>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
          {error}
        </div>
      )}

      {result && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
          Run complete →{" "}
          <a href={`#decision`} className="font-semibold underline">
            view results
          </a>
        </div>
      )}
    </div>
  );
}
