# Phase 8 — Security, reliability, observability and cost hardening

## Goal

Audit the real system and harden it before production-like hosting/CD.

## Security review

Verify:
- S3 public access fully blocked;
- Cognito/API JWT protections on every protected route;
- CORS explicit;
- presigned URL expiration and owner-scoped keys;
- file type/size limits;
- DynamoDB owner-scoped access patterns;
- Bedrock retrieval owner filter invariant;
- no cross-user metadata leakage;
- least-privilege Lambda roles by function;
- no runtime `*` permissions without documented justification;
- no secrets/tokens/presigned URLs in logs;
- prompt injection defenses;
- safe error messages.

## Reliability

Review:
- API/Lambda timeouts;
- SDK timeout/retry config;
- bounded polling;
- Bedrock call limits;
- ingestion conflict handling;
- DynamoDB conditional writes where useful;
- partial failures;
- idempotent-ish finalize/ingest behavior;
- no duplicate model calls caused by application retries.

## Observability

Use native CloudWatch first:
- structured logs with request/execution correlation IDs;
- Lambda native metrics;
- API Gateway metrics/logging as appropriate;
- useful ingestion/query status logs without document contents.

Do not publish document text to CloudWatch.

Evaluate a minimal alarm set. If alarms can create cost outside approved envelope, gate before deployment.

## Cost hardening

Create a current service cost inventory for:
- Cognito;
- API Gateway;
- Lambda;
- S3 documents;
- DynamoDB;
- Bedrock embeddings;
- Knowledge Base operations;
- S3 Vectors;
- Bedrock generation;
- CloudWatch;
- later frontend hosting.

Enforce application bounds such as:
- maximum upload size;
- maximum documents/user for development/demo if useful;
- maximum query length;
- maximum retrieved chunks;
- maximum one generation invocation/query;
- no unbounded ingestion loops.

## Tests

Add negative/security tests that encode all invariants, especially cross-user isolation.

## Acceptance criteria

- Security/cost audit has no unexplained critical findings.
- Logs are useful without sensitive content.
- System behavior under common failures is documented and tested.
