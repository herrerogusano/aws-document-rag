# Progress

Current phase: `1`
Status: `ready_to_start`

## Phase status

- [x] Phase 0 — Bootstrap, repo structure, local contracts and CI baseline
- [ ] Phase 1 — React application shell and mocked document workflow
- [ ] Phase 2 — Cognito authentication and protected API skeleton
- [ ] Phase 3 — Secure document upload with S3 + DynamoDB metadata
- [ ] Phase 4 — Bedrock Knowledge Base + S3 Vectors + embeddings
- [ ] Phase 5 — Ingestion lifecycle, metadata filtering and ownership isolation
- [ ] Phase 6 — RAG query pipeline with retrieval, generation and citations
- [ ] Phase 7 — Full-stack UX integration
- [ ] Phase 8 — Security, reliability, observability and cost hardening
- [ ] Phase 9 — Production frontend hosting and stable manual deployment
- [ ] Phase 10 — CI/CD evolution with GitHub OIDC and automated deployment
- [ ] Phase 11 — Demo, portfolio documentation, interview preparation and closure

## Last completed checks

- Planning bundle copied directly to repository root.
- Phase 0: `uv sync`, Ruff format/lint, mypy, pytest (2 passed), frontend lint/build, and `sam validate --lint` pass locally.

## Pending gate

Gate A — First AWS deployment (`pending`, not reached; Phase 2 earliest).

## Decisions that affect later phases

- Python 3.13 selected for the future Lambda runtime after official AWS support verification on 2026-08-27.
- CI remains entirely offline and credential-free until an approved later phase.
- Phase 0 SAM template contains only a conditionally disabled CloudFormation placeholder so it validates locally without defining active infrastructure.

## Phase 0 completion

- Resources created: none.
- Deployment state: no AWS deployment attempted.
- CI state: workflow added for backend, frontend, SAM validation, and static credential-pattern checking; remote CI pending first GitHub push/PR.
- Next phase: Phase 1 — React application shell and mocked document workflow.
