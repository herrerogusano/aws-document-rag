# Phase 0 — Bootstrap, repo structure, local contracts and CI baseline

## Goal

Create the project skeleton and establish CI from day one without touching AWS.

## Deliverables

- Initialize/verify repository `aws-document-rag`.
- Backend Python project managed by uv.
- React frontend project with current supported tooling.
- Basic SAM template that validates locally but creates no unapproved paid infrastructure.
- Application contracts/models for document metadata, ingestion status, query and citations.
- `AGENTS.md`, `PLAN.md`, plan files and progress tracking present in repo.
- CI workflow on PRs.

## Suggested structure

```text
frontend/
backend/
  src/aws_document_rag/
  tests/
infra/              # only if useful; otherwise keep template.yaml at root
docs/
  architecture/
  plan/
.github/workflows/
template.yaml
pyproject.toml
```

Do not force this exact structure if a cleaner initialized repo already exists.

## Backend baseline

- Python runtime must be a currently supported AWS Lambda runtime; verify official AWS docs before choosing.
- uv lockfile committed.
- pytest.
- lint/format/type tooling selected once and kept consistent.
- No real Boto3 calls in tests.

## Frontend baseline

- React with a modern build tool.
- Minimal routes/components only.
- TypeScript preferred if the project is being created from scratch.
- API/auth adapters should be injectable/mockable.

## CI baseline

PR CI should run, as applicable:
- backend dependency sync from lockfile;
- backend lint/format check/type check;
- backend unit tests;
- frontend install from lockfile;
- frontend lint/type/build/test if configured;
- `sam validate`;
- secret/static credential scan using lightweight repository tests/tools.

No AWS credentials. No Bedrock. No deploy.

## Architecture contracts

Define application-level models before AWS implementation:
- `DocumentRecord`;
- statuses such as `PENDING_UPLOAD`, `UPLOADED`, `INGESTING`, `READY`, `FAILED`;
- `QueryRequest`;
- `RetrievedChunk`;
- `Citation`;
- `QueryAnswer`.

Avoid over-modeling.

## Documentation

Create/update:
- README skeleton;
- architecture overview;
- decisions;
- local development guide.

## Acceptance criteria

- Fresh clone can install backend/frontend dependencies.
- Backend tests pass.
- Frontend builds.
- SAM validates locally.
- PR CI workflow exists and contains no AWS authentication/deployment.
- No secrets committed.

## Autonomous git workflow

Create branch, commit, push, PR and merge automatically after CI passes. No critical gate should be crossed in this phase.
