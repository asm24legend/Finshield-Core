"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getCase, getAgentRuns, getRiskAssessment, Case, AgentRun, RiskAssessment } from "@/lib/api";

const AGENT_LABELS: Record<string, string> = {
  kyc_agent: "KYC Verification",
  sanctions_agent: "Sanctions Screening",
  market_risk_agent: "Market Risk",
  aggregator_agent: "Final Aggregation",
};

const AGENT_ORDER = ["kyc_agent", "sanctions_agent", "market_risk_agent", "aggregator_agent"];

function StatusDot({ status }: { status: string | undefined }) {
  const color =
    status === "completed"
      ? "bg-green-500"
      : status === "running"
      ? "bg-amber-500 animate-pulse"
      : status === "failed"
      ? "bg-red-500"
      : "bg-slate-300";
  return <span className={`inline-block w-2.5 h-2.5 rounded-full ${color}`} />;
}

export default function CaseDetail() {
  const params = useParams();
  const caseId = params.id as string;

  const [caseData, setCaseData] = useState<Case | null>(null);
  const [risk, setRisk] = useState<RiskAssessment | null>(null);
  const [runs, setRuns] = useState<AgentRun[]>([]);

  useEffect(() => {
    let active = true;

    async function poll() {
  try {
    const [c, r, riskData] = await Promise.all([
      getCase(caseId),
      getAgentRuns(caseId),
      getRiskAssessment(caseId),
    ]);
    if (active) {
      setCaseData(c);
      setRuns(r);
      setRisk(riskData);
    }
  } catch (err) {
    console.error(err);
  }
}
    poll();
    const interval = setInterval(poll, 2000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [caseId]);

  const runByAgent = Object.fromEntries(runs.map((r) => [r.agent_name, r]));

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-10">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-lg font-semibold text-slate-900 mb-1">Case {caseId.slice(0, 8)}</h1>
        <p className="text-sm text-slate-500 mb-6">
          Status:{" "}
          <span className="font-medium text-slate-700">{caseData?.status ?? "loading..."}</span>
        </p>
        {risk && (
  <div className="mb-4 bg-white rounded-lg border border-slate-200 p-4 flex items-center justify-between">
    <div>
      <p className="text-xs text-slate-500">Risk score</p>
      <p className="text-2xl font-semibold text-slate-900">{risk.score}</p>
      <p className="text-xs text-slate-500 mt-1 max-w-sm">{risk.rationale}</p>
    </div>
    <span
      className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap ${
        risk.band === "low"
          ? "bg-green-100 text-green-800"
          : risk.band === "medium"
          ? "bg-amber-100 text-amber-800"
          : "bg-red-100 text-red-800"
      }`}
    >
      {risk.band.toUpperCase()}
    </span>
  </div>
)}

        <div className="bg-white rounded-lg border border-slate-200 divide-y divide-slate-100">
          {AGENT_ORDER.map((agentName) => {
            const run = runByAgent[agentName];
            return (
              <div key={agentName} className="p-4 flex items-start gap-3">
                <div className="mt-1">
                  <StatusDot status={run?.status} />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-800">
                    {AGENT_LABELS[agentName]}
                  </p>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {run?.status ?? "pending"}
                  </p>
                  {run?.output && (
                    <p className="text-xs text-slate-600 mt-2 bg-slate-50 rounded px-2 py-1.5">
                      {String(run.output.summary ?? JSON.stringify(run.output))}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </main>
  );
}