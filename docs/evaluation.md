# Semantic evaluation

`scripts/evaluate_ambiguous_rag.py` is a deliberately small live suite for the configured Nova Lite prompt. It sends only committed synthetic context and covers:

1. ambiguous before/after wording;
2. an elliptical question with one clear referent;
3. a question unsupported by the context;
4. conflicting source values;
5. a prompt-injection instruction embedded in document text.

The evaluator is not part of CI/CD because it invokes a paid model. It requires the explicit flag below and performs five calls for the full suite:

```powershell
uv run python scripts/evaluate_ambiguous_rag.py --live --region eu-west-1
```

After correcting a failed behavior, rerun only that case to avoid paying for unrelated repetitions:

```powershell
uv run python scripts/evaluate_ambiguous_rag.py --live --region eu-west-1 --case document_prompt_injection
```

Each run prints only the synthetic answer and pass/fail. Do not replace the fixtures with real documents or private questions. Extend the suite when a real failure reveals a general behavior class; avoid rules tailored to one sentence.

This suite measures a narrow generation contract, not full RAG quality. A production evaluation should separately measure retrieval recall, citation precision, faithfulness, multilingual behavior, latency, and per-query cost against a versioned dataset with human-reviewed expected evidence.
