# Phase 6 — RAG query pipeline with retrieval, generation and citations

## Goal

Answer authenticated questions using only relevant chunks from the current user's indexed documents.

## Pipeline

```text
question
→ validate/authenticate
→ Bedrock Knowledge Base Retrieve
   with owner_sub filter
→ normalize top chunks
→ bounded prompt
→ Bedrock Converse / chosen generation API
→ answer
→ citations
```

Keep retrieval and generation explicit in code so the RAG mechanism is understandable in interview.

## Retrieval

- Always apply `owner_sub` filter.
- Optionally support a `document_id` filter to ask about one selected document.
- Bound number of retrieved results.
- Do not return full raw Bedrock responses to frontend.
- Normalize source filename/document ID/location safely.

## Generation

- Choose a current Bedrock model available for the region/use case.
- Low/controlled temperature for grounded Q&A.
- Strict max output tokens.
- Prompt instructs model to answer from provided context only and state when context is insufficient.
- Retrieved document text is untrusted data, not instructions.
- Do not allow document prompt injection to override system/application instructions.

## Citations

`QueryAnswer` should include a concise answer plus citations referencing retrieved sources.

Do not invent page numbers unless retrieval metadata genuinely contains them.

## Critical Gate C

Before the first real generative query, present Gate C report and stop.

After approval, one small synthetic/approved query may be executed. Routine development queries remain bounded by the approved envelope.

## Failure behavior

- no retrieval results → honest insufficient-context answer without LLM call when practical;
- Bedrock retrieval error → sanitized API error;
- generation error → controlled failure; optionally deterministic extractive response if already designed and useful;
- no automatic retry that doubles model cost.

## Tests

- owner filter mandatory;
- optional document filter cannot broaden scope;
- prompt injection strings in documents remain data;
- retrieved chunk/token limits;
- zero-results behavior;
- citations map only to retrieved chunks;
- model invocation max one per query unless explicitly approved otherwise;
- no Bedrock calls in CI.

## Acceptance criteria

- Authenticated user can ask a question and receive a grounded answer with citation(s).
- User A cannot retrieve/generate from User B content.
- Cost per query is bounded/documented.
