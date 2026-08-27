# Phase 7 — Full-stack UX integration

## Goal

Replace remaining mocks and make the complete user journey coherent and usable.

## End-to-end journey

```text
sign in
→ see own documents
→ upload
→ see ingestion progress
→ READY
→ select all/one document
→ ask question
→ grounded answer + citations
```

## Frontend

Implement/refine:
- authentication guards;
- documents page;
- upload progress;
- ingestion status polling with bounded interval/backoff;
- ready/failed states;
- query form/chat-like history in browser state if useful;
- citations panel;
- clear insufficient-context state;
- logout/session-expired handling.

No need for permanent conversation history unless already justified.

## API client

- One centralized authenticated API client.
- Token refresh handled through auth library/flow.
- No tokens in local logs.
- Abort/timeout support.
- Typed API contracts where practical.

## UX security

Frontend hiding is not authorization. Backend remains authoritative.

Do not expose:
- S3 keys unless needed;
- Cognito `sub` in visible UI;
- Knowledge Base IDs;
- model IDs unless part of a developer diagnostics screen not shipped publicly.

## Tests

- full mocked component flow;
- API contract tests;
- session expiration;
- upload failure;
- ingestion failure;
- query failure;
- no-result response;
- citations.

If a lightweight local end-to-end browser test framework already exists, use it; do not add a heavy framework solely for appearance.

## Acceptance criteria

- Local frontend against deployed development backend completes the full flow.
- No mock service remains in the normal production path.
- CI tests/build remain green.
