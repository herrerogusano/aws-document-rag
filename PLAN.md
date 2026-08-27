# AWS Document RAG — Master Plan

## Project

Proposed repository: `aws-document-rag`

Goal: build a production-shaped full-stack RAG application where authenticated users upload documents and ask questions grounded only in their own documents.

Target architecture:

```text
React
  ↓
Amazon Cognito
  ↓ JWT
API Gateway HTTP API
  ↓
Lambda (Python)
  ├─ S3 source documents
  ├─ DynamoDB document metadata/status
  ├─ Bedrock Knowledge Bases
  │    └─ S3 Vectors + embedding model
  └─ Bedrock Runtime LLM
        ↓
Answer + citations
```

Frontend production hosting is introduced only after the full flow works manually:

```text
CloudFront
  ↓
private S3 frontend bucket
```

CI starts in Phase 0 and evolves continuously. CD is introduced only after manual deployment is stable.

## Why this architecture

- Cognito handles user identity and JWTs.
- API Gateway validates JWTs before protected Lambda routes.
- Presigned S3 uploads keep document bytes out of API Gateway/Lambda.
- DynamoDB stores application metadata and ingestion state, not embeddings.
- Bedrock Knowledge Bases manages chunking/embedding/retrieval.
- S3 Vectors is the preferred vector store for this learning project because it is serverless and suited to infrequent RAG queries; Codex must re-check regional availability and current pricing before creating it.
- Retrieval and generation stay conceptually separate: retrieve relevant chunks first, then generate an answer with citations.
- Per-user metadata filtering is mandatory so one user cannot retrieve another user's documents.

## Global constraints

- Primary AWS region: `eu-west-1` unless a verified service limitation forces a documented change.
- Backend: Python + uv.
- Infrastructure: AWS SAM / CloudFormation unless a phase explicitly says otherwise.
- Frontend: React.
- Cost policy: zero accidental cost. Any potentially billable or unknown-cost AWS resource/action requires a cost preview before first enablement.
- Never store AWS access keys, Cognito passwords, test-user passwords, tokens, or sensitive user data in Git.
- Use least privilege IAM.
- No `AdministratorAccess` for runtime or CI/CD roles.
- Do not reuse runtime dependencies from previous exercises.
- CI never calls real AWS, Bedrock, or Cognito.
- No production-like CD until manual deployment is proven repeatable.

## Autonomous execution model

Codex should execute phases in numerical order using `AGENTS.md` as the permanent operating policy.

For each phase:

1. Read `PLAN.md`, `AGENTS.md`, `docs/plan/PROGRESS.md`, `docs/plan/GATES.md` and the current phase file.
2. Create a branch `phase/<NN>-<short-name>`.
3. Implement the phase.
4. Run all required checks.
5. Update docs and `PROGRESS.md`.
6. Commit with a clear conventional commit message.
7. Push the phase branch and create a PR.
8. Wait for CI.
9. If CI is green, acceptance criteria pass, and no critical gate is pending, merge the PR autonomously.
10. Pull/update `main`, mark the phase complete, and start the next phase.

If a critical gate is reached, prepare everything up to the gate and stop before the irreversible/billable/sensitive action.

## Phase index

- Phase 0 — Bootstrap, repo structure, local contracts and CI baseline
- Phase 1 — React application shell and mocked document workflow
- Phase 2 — Cognito authentication and protected API skeleton
- Phase 3 — Secure document upload with S3 + DynamoDB metadata
- Phase 4 — Bedrock Knowledge Base + S3 Vectors + embeddings
- Phase 5 — Ingestion lifecycle, metadata filtering and ownership isolation
- Phase 6 — RAG query pipeline with retrieval, generation and citations
- Phase 7 — Full-stack UX integration
- Phase 8 — Security, reliability, observability and cost hardening
- Phase 9 — Production frontend hosting and stable manual deployment
- Phase 10 — CI/CD evolution with GitHub OIDC and automated deployment
- Phase 11 — Demo, portfolio documentation, interview preparation and closure

See `docs/plan/phases/` for the detailed contract of every phase.
