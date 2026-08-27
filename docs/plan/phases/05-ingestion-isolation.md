# Phase 5 — Ingestion lifecycle, metadata filtering and ownership isolation

## Goal

Make ingestion a controlled application workflow and prove multi-user isolation before adding generation.

## Lifecycle

Implement a clear state machine such as:

```text
PENDING_UPLOAD
→ UPLOADED
→ INGESTING
→ READY
or FAILED
```

Do not expose raw AWS status objects to frontend.

## Ingestion API

Create/refine an authenticated ingestion/finalization route.

Responsibilities:
- verify document belongs to current Cognito `sub`;
- verify expected S3 object exists and is within allowed key;
- create/update metadata sidecar with `owner_sub` and `document_id`;
- start or coordinate Knowledge Base ingestion using bounded calls;
- update DynamoDB status;
- handle in-progress/conflict state safely.

Avoid starting repeated ingestion jobs merely because frontend polls.

## Status tracking

Frontend polls a document-status API or uses another simple bounded mechanism. Do not add WebSockets/AppSync just for status.

Backend may reconcile Bedrock ingestion state when necessary but must avoid high-frequency polling and unbounded AWS calls.

## Mandatory retrieval isolation test

Create at least two synthetic users/owners in tests:
- User A document;
- User B document.

For User A's retrieval request, the Bedrock retrieval configuration must always include a metadata filter equivalent to `owner_sub == A`.

A repository test must fail if retrieval can be constructed without owner filtering.

## Security invariants

- owner comes from JWT `sub` only;
- user-supplied document ID is always combined with owner scope;
- sidecar metadata cannot be supplied directly by browser;
- browser cannot set `owner_sub`;
- ingestion errors do not leak S3 keys/ARNs unnecessarily.

## Reliability

Handle:
- already-ingesting document;
- ingestion service throttling;
- missing S3 object;
- unsupported/corrupt document;
- Bedrock permission failure;
- partial metadata updates.

No aggressive retries.

## Tests

- state transitions;
- duplicate ingestion request;
- owner mismatch;
- metadata creation;
- mandatory retrieval filter builder;
- failure/status sanitization.

## Acceptance criteria

- Upload → ingest → READY works for approved test document.
- Isolation is enforced in code and tests before generation exists.
