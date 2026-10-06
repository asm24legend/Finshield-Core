const API_BASE = "http://localhost:8000";

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

export interface AgentRun {
  agent_name: string;
  status: string;
  output: Record<string, unknown> | null;
  started_at: string;
  finished_at: string | null;
}

export async function createEntity(data: {
  name: string;
  entity_type: string;
  jurisdiction?: string;
}): Promise<Entity> {
  const res = await fetch(`${API_BASE}/entities`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create entity");
  return res.json();
}

export async function createCase(data: {
  entity_id: string;
  case_type: string;
}): Promise<Case> {
  const res = await fetch(`${API_BASE}/cases`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create case");
  return res.json();
}

export async function getCase(caseId: string): Promise<Case> {
  const res = await fetch(`${API_BASE}/cases/${caseId}`);
  if (!res.ok) throw new Error("Failed to fetch case");
  return res.json();
}

export async function getAgentRuns(caseId: string): Promise<AgentRun[]> {
  const res = await fetch(`${API_BASE}/cases/${caseId}/agent-runs`);
  if (!res.ok) throw new Error("Failed to fetch agent runs");
  return res.json();
}
export interface RiskAssessment {
  score: number;
  band: string;
  rationale: string;
}

export async function getRiskAssessment(caseId: string): Promise<RiskAssessment | null> {
  const res = await fetch(`${API_BASE}/cases/${caseId}/risk-assessment`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("Failed to fetch risk assessment");
  return res.json();
}

export function getReportUrl(caseId: string): string {
  return `${API_BASE}/cases/${caseId}/report`;
}

export interface Review {
  id: string;
  decision: string;
  reviewer_note: string | null;
  reviewed_at: string;
}

export async function submitReview(caseId: string, decision: string, note?: string): Promise<Review> {
  const res = await fetch(`${API_BASE}/cases/${caseId}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision, reviewer_note: note }),
  });
  if (!res.ok) throw new Error("Failed to submit review");
  return res.json();
}

export async function getReview(caseId: string): Promise<Review | null> {
  const res = await fetch(`${API_BASE}/cases/${caseId}/review`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("Failed to fetch review");
  return res.json();
}