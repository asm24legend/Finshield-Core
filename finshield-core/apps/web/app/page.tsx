"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createEntity, createCase } from "@/lib/api";

export default function Home() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [entityType, setEntityType] = useState("corporation");
  const [jurisdiction, setJurisdiction] = useState("");
  const [caseType, setCaseType] = useState("loan_application");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const entity = await createEntity({
        name,
        entity_type: entityType,
        jurisdiction: jurisdiction || undefined,
      });
      const newCase = await createCase({
        entity_id: entity.id,
        case_type: caseType,
      });
      router.push(`/cases/${newCase.id}`);
    } catch (err) {
      setError("Something went wrong submitting the case. Is the API running?");
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-white rounded-lg shadow-sm border border-slate-200 p-8">
        <h1 className="text-xl font-semibold text-slate-900 mb-1">FinShield Core</h1>
        <p className="text-sm text-slate-500 mb-6">Submit a case for automated review</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Entity name
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
              placeholder="Acme Corp"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Entity type
            </label>
            <select
              value={entityType}
              onChange={(e) => setEntityType(e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
            >
              <option value="corporation">Corporation</option>
              <option value="individual">Individual</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Jurisdiction (optional)
            </label>
            <input
              type="text"
              value={jurisdiction}
              onChange={(e) => setJurisdiction(e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
              placeholder="US-DE"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Case type
            </label>
            <select
              value={caseType}
              onChange={(e) => setCaseType(e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
            >
              <option value="loan_application">Loan application</option>
              <option value="sanctions_flag">Sanctions flag</option>
            </select>
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-slate-900 text-white rounded-md py-2 text-sm font-medium hover:bg-slate-800 disabled:opacity-50"
          >
            {loading ? "Submitting..." : "Submit case"}
          </button>
        </form>
      </div>
    </main>
  );
}