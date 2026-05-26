export type Determination = "approve" | "deny" | "human_review";
export type GuardrailStatus = "pass" | "warning" | "fail";
export type CaseStatus = "pending" | "approved" | "denied" | "under_review";
export type EvalStatus = "pass" | "warning" | "fail";

export interface CaseListItem {
  id: string;
  member_id: string;
  provider_id: string;
  age_band: string;
  service_code: string;
  service_description: string;
  status: CaseStatus;
  tags: string[];
  created_at: string;
}

export interface CaseDetail extends CaseListItem {
  diagnosis_codes: string[];
  clinical_notes_summary: string | null;
  policy_document_ids: string[];
}

export interface PolicyClause {
  id: string;
  document_id: string;
  section: string;
  clause_text: string;
  tags: string[];
  determination_hint: string | null;
}

export interface PolicyDocument {
  id: string;
  title: string;
  payer_code: string;
  effective_date: string;
  description: string | null;
  clauses: PolicyClause[];
}

export interface PolicyContext {
  case_id: string;
  policy_documents: PolicyDocument[];
}

export interface PolicyCitation {
  clause_id: string;
  document_id: string;
  section: string;
  relevance_score: number;
}

export interface DecisionRun {
  run_id: string;
  case_id: string;
  determination: Determination;
  confidence_score: number;
  policy_citations: PolicyCitation[];
  rationale_summary: string;
  guardrail_status: GuardrailStatus;
  guardrail_reasons: string[];
  latency_ms: number;
  llm_enhanced: boolean;
  created_at: string;
}

export interface TraceEvent {
  id: string;
  step_name: string;
  status: string;
  started_at: string;
  ended_at: string;
  input_summary: string;
  output_summary: string;
  artifact_refs: string[];
  warning_flags: string[];
  sequence: number;
}

export interface Trace {
  run_id: string;
  events: TraceEvent[];
}

export interface EvalResult {
  run_id: string;
  policy_coverage_score: number;
  citation_presence: boolean;
  contradiction_flag: boolean;
  missing_evidence_flag: boolean;
  escalation_correctness: boolean;
  overall_eval_status: EvalStatus;
}

export interface ReviewQueueItem {
  id: string;
  run_id: string;
  case_id: string;
  reason: string;
  priority: string;
  assigned_to: string | null;
  resolved: boolean;
  created_at: string;
}
