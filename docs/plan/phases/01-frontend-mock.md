# Phase 1 — React application shell and mocked document workflow

## Goal

Build the user-facing flow locally before connecting AWS.

## User journey

```text
open app
→ sign-in placeholder/auth abstraction
→ documents screen
→ choose document
→ mocked upload
→ document becomes READY
→ ask question
→ mocked grounded answer + citations
```

## Scope

- App shell/navigation.
- Sign-in/sign-out UI through an auth interface, still mocked.
- Documents list.
- Upload control with file validation.
- Ingestion status component.
- Query/chat area.
- Citation component linking an answer to source filename/page/section when available.
- Loading/error/empty states.

## Important constraints

- Do not implement real Cognito yet.
- Do not upload anywhere.
- Do not add a generic chat UI that can answer without documents.
- Answers must conceptually be grounded in retrieved sources.

## Frontend boundaries

Create abstractions such as:
- `AuthProvider` / auth client;
- `DocumentsApi`;
- `QueryApi`.

Mock implementations power local development and tests.

## Tests

Add frontend tests for:
- unauthenticated vs authenticated state;
- upload validation;
- document status transitions;
- question submission;
- citations rendering;
- API error states.

Extend CI accordingly.

## Acceptance criteria

- A reviewer can understand the entire future RAG flow without AWS.
- No hardcoded AWS IDs/endpoints.
- Frontend build/tests pass in CI.

## Git

Autonomous branch/commit/PR/merge when green.
