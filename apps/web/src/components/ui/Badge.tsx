import clsx from "clsx";
import type { CaseStatus, Determination, GuardrailStatus, EvalStatus } from "@/types";

type Variant = "neutral" | "approve" | "deny" | "review" | "pass" | "warning" | "fail" | "pending";

const variantClasses: Record<Variant, string> = {
  neutral: "bg-slate-100 text-slate-700",
  approve: "bg-emerald-100 text-emerald-800",
  deny: "bg-red-100 text-red-800",
  review: "bg-amber-100 text-amber-800",
  pass: "bg-emerald-100 text-emerald-800",
  warning: "bg-amber-100 text-amber-800",
  fail: "bg-red-100 text-red-800",
  pending: "bg-slate-100 text-slate-600",
};

interface BadgeProps {
  children: React.ReactNode;
  variant?: Variant;
  className?: string;
}

export function Badge({ children, variant = "neutral", className }: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide",
        variantClasses[variant],
        className
      )}
    >
      {children}
    </span>
  );
}

export function statusBadgeVariant(status: CaseStatus): Variant {
  const map: Record<CaseStatus, Variant> = {
    pending: "pending",
    approved: "approve",
    denied: "deny",
    under_review: "review",
  };
  return map[status] ?? "neutral";
}

export function determinationVariant(d: Determination): Variant {
  const map: Record<Determination, Variant> = {
    approve: "approve",
    deny: "deny",
    human_review: "review",
  };
  return map[d] ?? "neutral";
}

export function guardrailVariant(g: GuardrailStatus): Variant {
  const map: Record<GuardrailStatus, Variant> = {
    pass: "pass",
    warning: "warning",
    fail: "fail",
  };
  return map[g] ?? "neutral";
}

export function evalVariant(e: EvalStatus): Variant {
  const map: Record<EvalStatus, Variant> = {
    pass: "pass",
    warning: "warning",
    fail: "fail",
  };
  return map[e] ?? "neutral";
}
