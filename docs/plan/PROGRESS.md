# Progress

Current phase: `5`
Status: `in_progress`

## Phase status

- [x] Phase 0 — Bootstrap, repo structure, local contracts and CI baseline
- [x] Phase 1 — React application shell and mocked document workflow
- [x] Phase 2 — Cognito authentication and protected API skeleton
- [x] Phase 3 — Secure document upload with S3 + DynamoDB metadata
- [x] Phase 4 — Bedrock Knowledge Base + S3 Vectors + embeddings
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
- Phase 3: all offline checks pass (Ruff, mypy, 13 pytest tests, SAM lint/build, frontend lint, 2 Vitest tests and production build). A real authenticated TXT upload completed through a regional presigned URL; private S3 object, Cognito owner match, list persistence and lifecycle status were verified.
- Phase 4: Gate B approved; one Knowledge Base, S3 data source and private SSE-S3 vector bucket/index deployed in `eu-west-1`. One sub-10-KiB document ingested and one owner-filtered retrieval returned one result with matching owner/document metadata. No generation occurred.

## Pending gate

Gate C — First real generative RAG call (`pending`). Phases 5 and retrieval-only portions of Phase 6 may proceed, but no generative model invocation may occur before approval.

## Decisions that affect later phases

- Python 3.13 selected for the future Lambda runtime after official AWS support verification on 2026-08-27.
- CI remains entirely offline and credential-free until an approved later phase.
- Phase 0 SAM template contains only a conditionally disabled CloudFormation placeholder so it validates locally without defining active infrastructure.
- React is intentionally backed by injectable local mock adapters until the Phase 2 Cognito/API boundary is approved.
- Gate A deployed Cognito, a public SPA client without secret, a JWT-authorized HTTP API, and a Lambda `/me` in `eu-west-1`; no user accounts or document data were created.
- The Cognito Hosted UI prefix was deployed after addendum approval. The first domain name was rejected because AWS reserves `aws` in prefix domains; CloudFormation rolled back that resource only, and the corrected prefix deployed successfully.

## Phase 3 completion

- Resources created: one private SSE-S3 document bucket with Block Public Access and localhost-only upload CORS; one DynamoDB on-demand metadata table; one authenticated document Lambda and owner-scoped API routes.
- Runtime flow: authenticated presign, direct browser-to-S3 upload, upload confirmation, list and get. Document bytes never pass through Lambda/API Gateway.
- Security validation: server-generated Cognito-`sub` object keys, five-minute presigned PUT, private object confirmed, metadata owner matched the real login, and other-owner reads are covered by offline tests.
- Incident resolved: S3 URLs are generated directly against the regional endpoint to prevent a browser-blocked `307` redirect. Five metadata-only records left by failed attempts were removed after confirming that no S3 objects existed; the successful document remains.
- Deployment state: Phase 3 resources and routes are live in `eu-west-1`; the local frontend restores its Cognito session and reloads persisted document metadata.
- Next phase: Phase 4 local design and tests, then Gate B before any Bedrock Knowledge Base, S3 Vectors, embedding ingestion or retrieval call.

## Phase 4 completion

- Gate B: approved on 2026-08-27 within the limits in `GATE_B_REPORT.md`.
- Resources created: one Bedrock Knowledge Base, one S3 data source, one SSE-S3 vector bucket, one 1,024-dimension cosine vector index and one least-privilege Bedrock service role.
- Configuration: Titan Text Embeddings V2, 300-token fixed chunks, 20% overlap, standard parser, no OpenSearch Serverless and no generative model.
- Isolation: filter-only `owner_sub` and `document_id` sidecar metadata; retrieval configuration requires an exact owner equality filter.
- Live validation: one document scanned/indexed successfully; one retrieval-only call returned one result and its sanitized metadata matched both expected identifiers.
- Deployment note: the first vector-bucket attempt rolled back because the generated name used a reserved prefix; a bounded explicit name fixed the issue and the second deployment completed.
- Next phase: Phase 5 ingestion lifecycle, status reconciliation and multi-owner isolation tests.

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
