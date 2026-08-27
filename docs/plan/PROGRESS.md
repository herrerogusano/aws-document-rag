# Progress

Current phase: `3`
Status: `blocked_by_gate_a_scope_review`

## Phase status

- [x] Phase 0 — Bootstrap, repo structure, local contracts and CI baseline
- [x] Phase 1 — React application shell and mocked document workflow
- [x] Phase 2 — Cognito authentication and protected API skeleton
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
- Phase 1: frontend lint, Vitest (2 passed), and production build pass locally.
- Phase 2: Cognito/API Gateway/Lambda and Cognito Hosted UI prefix deployed after Gate A approval; synthetic JWT handler tests plus unauthenticated endpoint, CORS, and Hosted UI availability checks pass. One test user was created with invitation delivery; real sign-in awaits its first password-change completion.
- Phase 2 completion: the real Authorization Code + PKCE browser flow completed and the local frontend confirmed that `/me` accepted its JWT; no token was logged or stored outside browser session storage.

## Pending gate

Gate A — First AWS deployment (`approved and deployed 2026-08-27`); Managed Login domain addendum approved and deployed. Test-user credential gate approved and actioned; awaiting user-controlled first sign-in/password change.

## Decisions that affect later phases

- Python 3.13 selected for the future Lambda runtime after official AWS support verification on 2026-08-27.
- CI remains entirely offline and credential-free until an approved later phase.
- Phase 0 SAM template contains only a conditionally disabled CloudFormation placeholder so it validates locally without defining active infrastructure.
- React is intentionally backed by injectable local mock adapters until the Phase 2 Cognito/API boundary is approved.
- Gate A deployed Cognito, a public SPA client without secret, a JWT-authorized HTTP API, and a Lambda `/me` in `eu-west-1`; no user accounts or document data were created.
- The Cognito Hosted UI prefix was deployed after addendum approval. The first domain name was rejected because AWS reserves `aws` in prefix domains; CloudFormation rolled back that resource only, and the corrected prefix deployed successfully.

## Phase 2 completion

- Resources created: Cognito User Pool and public SPA client, Cognito Hosted UI prefix, API Gateway HTTP API, Lambda `/me`, Lambda execution role and CloudWatch log group (all in `eu-west-1`).
- Gates approved: Gate A and its Managed Login-domain addendum; one test-user credential created without committing or logging its password.
- CI state: expanded frontend PKCE code remains offline-testable; PR CI has no AWS credentials or live authentication.
- Deployment state: manual SAM deployment succeeded; unauthenticated API returns `401`, CORS is restricted to the local origin, and one real browser JWT was accepted by `/me`.
- Limitation: no production frontend origin yet; localhost is the only allowed callback/CORS origin.
- Next phase: Phase 3 — private S3 uploads and DynamoDB metadata. Its infrastructure must remain within the approved cost/IAM envelope or be gated before deployment.

## Phase 0 completion

- Resources created: none.
- Deployment state: no AWS deployment attempted.
- CI state: workflow added for backend, frontend, SAM validation, and static credential-pattern checking; remote CI pending first GitHub push/PR.
- Next phase: Phase 1 — React application shell and mocked document workflow.

## Phase 1 completion

- Resources created: none.
- Deployment state: no AWS deployment attempted.
- CI state: extended with offline Vitest coverage for mock sign-in and upload validation; remote CI pending Phase 1 PR.
- Next phase: Phase 2 — Cognito authentication and protected API skeleton (Gate A).
