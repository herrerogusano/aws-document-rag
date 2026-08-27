# Progress

Current phase: `10`
Status: `phase_9_complete`

## Phase status

- [x] Phase 0 — Bootstrap, repo structure, local contracts and CI baseline
- [x] Phase 1 — React application shell and mocked document workflow
- [x] Phase 2 — Cognito authentication and protected API skeleton
- [x] Phase 3 — Secure document upload with S3 + DynamoDB metadata
- [x] Phase 4 — Bedrock Knowledge Base + S3 Vectors + embeddings
- [x] Phase 5 — Ingestion lifecycle, metadata filtering and ownership isolation
- [x] Phase 6 — RAG query pipeline with retrieval, generation and citations
- [x] Phase 7 — Full-stack UX integration
- [x] Phase 8 — Security, reliability, observability and cost hardening
- [x] Phase 9 — Production frontend hosting and stable manual deployment
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
- Phase 5: 29 backend tests pass with owner mismatch, duplicate ingestion, state reconciliation, size-bound and two-owner retrieval-isolation coverage. The deployed lifecycle reconciled the approved document to `READY` without an additional ingestion job.

## Pending gate

Gate D — production frontend hosting. Phase 7 and Phase 8 may proceed before that gate.

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

## Phase 5 completion

- API lifecycle: authenticated finalize writes the server-owned metadata sidecar; authenticated ingest verifies owner, source object, sidecar, status and the approved 100-KiB ceiling before starting an idempotent job.
- State machine: `PENDING_UPLOAD → UPLOADED → INGESTING → READY`, with sanitized `FAILED` reconciliation and bounded status polling.
- Reliability: duplicate starts return conflict, completed documents are idempotent, incomplete uploads are rejected, Bedrock/DynamoDB details are not exposed and polling does not restart ingestion.
- Isolation: owner always comes from JWT `sub`; document reads combine owner and document ID; retrieval configuration cannot be built without the exact owner filter. Offline tests include distinct owner-A and owner-B documents.
- Live validation: the already approved ingestion job was reconciled through the deployed Lambda and the document metadata transitioned to `READY`; no second ingestion was started.
- Next phase: Phase 6 retrieval and cited generation. Gate C pricing/model bounds must be documented before the first generative call.

## Phase 6 completion

- Gate C: approved on 2026-08-27 within the exact limits in `GATE_C_REPORT.md` through the user's explicit autonomous-gate delegation.
- Query pipeline: authenticated `POST /query` performs owner-filtered Knowledge Base retrieval, drops mismatched metadata, bounds context, invokes Nova Micro once and cites only retrieved documents.
- Prompt-injection defense: retrieved text is serialized as untrusted data under a system instruction that rejects embedded commands and secret requests.
- Cost bounds: at most five 2,000-character chunks, a 1,000-character question and 256 generated tokens; zero results skip generation and no automatic retry is configured.
- Live validation: the first Gate C query returned HTTP 200, a non-empty answer and one citation matching the READY document. No answer text or source content was logged.
- Verification: 39 backend tests, mypy, Ruff, SAM lint/build, frontend lint, two frontend tests and the production frontend build pass.
- Next phase: Phase 7 full-stack UX integration and browser-level validation.

## Phase 7 completion

- Replaced the production-path document/query adapters with one typed authenticated API client featuring request timeouts, one refresh-token retry and explicit expired-session handling.
- Added all/one-document query scope, bounded upload/indexing progress, READY/FAILED states, query progress, insufficient-evidence presentation and citation chips.
- Preserved a separate mock path only for credential-free local tests; configured development uses the deployed APIs.
- Visual direction remains editorial and source-first, with corrected global CSS precedence, accessible focus states, reduced-motion support and responsive layouts.
- Browser validation at 1280 px and 390 px confirmed the intended typography, contrast and no horizontal overflow.
- Verification: frontend lint, six Vitest tests and production build pass; tests cover the full mock journey, typed API mapping, citations, document scope and session expiry.
- Next phase: Phase 8 security, reliability, observability and cost hardening.

## Phase 8 completion

- The security and current-cost inventory is recorded in `PHASE_08_AUDIT.md`; no unexplained critical finding remains.
- Deployed exact SDK timeouts/retries, JSON logs, 14-day Lambda/API log retention, API throttling, a 100-call monthly generation counter, 20-document/100-KiB limits and non-regressing finalize behavior.
- Tightened application roles to exact operations/resources. Live inspection found no wildcard action or wildcard resource in the document, query or Knowledge Base inline policies.
- Live validation confirmed all seven routes remain JWT protected, QueryFunction has a 30-second timeout, the malformed request returned 400, its structured event appeared and its sentinel private content did not.
- The first concurrency-reservation deployment rolled back because of the account quota; removing that unsupported reservation allowed the bounded controls to deploy successfully.
- Verification: 45 backend tests, mypy, Ruff, SAM lint/build, six frontend tests, frontend lint/build and live post-deployment checks pass.
- Next phase: Gate D report and production-like frontend hosting.

## Phase 9 completion

- Gate D: approved on 2026-08-27 within `GATE_D_REPORT.md` through the user's explicit autonomous-gate delegation.
- Deployed one CloudFront distribution with HTTPS redirect/TLS 1.2+, OAC-signed access to a separate encrypted private S3 artifact bucket, exact source-ARN bucket policy, SPA fallback, cache policy and security headers.
- Cognito callback/logout, API CORS and document upload CORS now include the exact generated CloudFront origin while retaining localhost development.
- Built the frontend from public stack outputs, uploaded hashed assets as immutable and `index.html` as no-cache, then submitted one bounded invalidation. No object deletion occurred.
- Live smoke validation returned HTTPS 200, referenced the production bundle, included CSP/HSTS/content-type/frame headers, confirmed direct unsigned S3 returned 403, all four public-access blocks were true, auth callbacks/logout and API CORS matched, and CloudFront/stack were deployed/complete.
- `scripts/deploy-frontend.ps1` and `docs/manual-deployment.md` define the repeatable non-destructive manual path and rollback.
- The full backend lifecycle and bounded cited generation were already validated in Phases 3–8; hosting introduced no extra ingestion or model call.
- Verification: 48 backend tests, SAM lint/build, frontend lint, six tests/build, PowerShell parse check and live hosting checks pass.
- Next phase: Gate E report, GitHub OIDC bootstrap and first automatic deployment.

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
