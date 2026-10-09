"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listCases, CaseSummary } from "@/lib/api";

const BAND_STYLE: Record<string, string> = {
  low: "bg-green-100 text-green-800",
  medium: "bg-amber-100 text-amber-800",
  high: "bg-red-100 text-red-800",
};

export default function CaseList() {
  const [cases, setCases] = useState<CaseSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listCases()
      .then(setCases)
      .catch(() => setError("Could not load cases. Is the API running?"));
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-10">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-lg font-semibold text-slate-900">Cases</h1>
          <Link href="/" className="text-sm text-slate-600 underline hover:text-slate-900">
            New case
          </Link>
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}
        {!cases && !error && <p className="text-sm text-slate-500">Loading...</p>}
        {cases && cases.length === 0 && <p className="text-sm text-slate-500">No cases yet.</p>}

        {cases && cases.length > 0 && (
          <div className="bg-white rounded-lg border border-slate-200 divide-y divide-slate-100">
            {cases.map((c) => (
              <Link
                key={c.id}
                href={`/cases/${c.id}`}
                className="flex items-center justify-between p-4 hover:bg-slate-50"
              >
                <div>
                  <p className="text-sm font-medium text-slate-800">{c.entity_name}</p>
                  <p className="text-xs text-slate-500">
                    {c.case_type.replace("_", " ")} · {new Date(c.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {c.review_decision && (
                    <span className="text-xs text-slate-500">reviewed: {c.review_decision}</span>
                  )}
                  {c.band ? (
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${BAND_STYLE[c.band] ?? ""}`}
                    >
                      {c.band.toUpperCase()} {c.score}
                    </span>
                  ) : (
                    <span className="text-xs text-slate-400">{c.status}</span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}