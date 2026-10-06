## Known Limitations (honest disclosures)
- This is a demo system, not a certified AML compliance product.
- Sanctions screening uses name-only fuzzy matching; real screening requires
  additional identity attributes (DOB, address, ID numbers).
- Market Risk agent uses a fixed demo stock symbol (AAPL) since not every
  applicant has a public ticker; a production system needs real symbol lookup.
- LLM-based agents use a small local model (Llama 3.1 8B via Ollama) for
  cost-free local inference; larger hosted models would likely produce more
  consistent structured output and more reliable instruction-following
  (e.g. the MASCA paper found hierarchical multi-agent systems combining a
  larger reasoning model with a smaller efficient model outperformed either alone).
- LLM-based credit/risk assessment is a studied source of bias (see MASCA,
  arXiv:2507.22758) — this demo does not implement bias auditing; a
  production system would need counterfactual fairness testing.