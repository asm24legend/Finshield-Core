const API_BASE = "http://localhost:8000";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY ?? "";

function authHeaders(extra: Record<string, string> = {}): Record<string, string> {
  return { "x-api-key": API_KEY, ...extra };
}

export interface Entity {
  id: string;
  name: string;
  entity_type: string;
  jurisdiction: string | null;
  created_at: string;
}

export interface Case {
  id: string;
  entity_id: string;
  case_type: string;
  status: string;
  created_at: string;
}

export interface CaseSummary {
  id: string;
  entity_name: string;
  case_type: string;
  status: string;
  band: string | null;
  score: number | null;
  review_decision: string | null;
  created_at: string;
}

export interface AgentRun {
  agent_name: string;
  status: string;
  output: Record<string, unknown> | null;
  started_at: string;
  finished_at: string | null;
}

export interface RiskAssessment {
  score: number;
  band: string;
  rationale: string;
}

export interface Review {
  id: string;
  decision: string;
  reviewer_note: string | null;
  reviewed_at: string;
}

export async function createEntity(data: {
  name: string;
  entity_type: string;
  jurisdiction?: string;
}): Promise<Entity> {
  const res = await fetch(`${API_BASE}/entities`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create entity");
  return res.json();
}

export async function createCase(data: { entity_id: string; case_type: string }): Promise<Case> {
  const res = await fetch(`${API_BASE}/cases`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create case");
  return res.json();
}

export async function listCases(): Promise<CaseSummary[]> {
  const res = await fetch(`${API_BASE}/cases`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Failed to list cases");
  return res.json();
}

export async function getCase(caseId: string): Promise<Case> {
  const res = await fetch(`${API_BASE}/cases/${caseId}`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Failed to fetch case");
  return res.json();
}

export async function getAgentRuns(caseId: string): Promise<AgentRun[]> {
  const res = await fetch(`${API_BASE}/cases/${caseId}/agent-runs`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Failed to fetch agent runs");
  return res.json();
}

export async function getRiskAssessment(caseId: string): Promise<RiskAssessment | null> {
  const res = await fetch(`${API_BASE}/cases/${caseId}/risk-assessment`, { headers: authHeaders() });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("Failed to fetch risk assessment");
  return res.json();
}

export async function submitReview(caseId: string, decision: string, note?: string): Promise<Review> {
  const res = await fetch(`${API_BASE}/cases/${caseId}/review`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ decision, reviewer_note: note }),
  });
  if (!res.ok) throw new Error("Failed to submit review");
  return res.json();
}

export async function getReview(caseId: string): Promise<Review | null> {
  const res = await fetch(`${API_BASE}/cases/${caseId}/review`, { headers: authHeaders() });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("Failed to fetch review");
  return res.json();
}

export async function downloadReport(caseId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/cases/${caseId}/report`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Failed to download report");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `case_${caseId}_report.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}