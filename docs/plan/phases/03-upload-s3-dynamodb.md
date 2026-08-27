# Phase 3 — Secure document upload with S3 + DynamoDB metadata

## Goal

Allow an authenticated user to upload a document securely without proxying document bytes through Lambda/API Gateway.

## Target flow

```text
React
→ POST /documents/presign
→ Lambda validates request/owner
→ DynamoDB DocumentRecord(PENDING_UPLOAD)
→ presigned S3 PUT
→ browser uploads directly to private S3
→ finalize/status API
```

## S3

- Private source-document bucket.
- Block Public Access enabled.
- Server-generated owner-scoped object keys, e.g. logical pattern `users/<sub>/documents/<document_id>/source.<ext>`.
- Do not let browser choose arbitrary bucket keys.
- Presigned PUT with short expiration.
- Restrict supported content type/extensions and maximum object size using the best mechanism supported by the selected upload approach.
- Encryption at rest with S3-managed encryption unless a customer-managed KMS key is clearly justified.
- No public website configuration.

## DynamoDB

Store application metadata only, not document text or embeddings.

Suggested logical access pattern:
- partition by authenticated user;
- sort by document ID;
- fields: document ID, filename display value, S3 key, status, timestamps, optional ingestion job metadata, safe error code.

Use on-demand billing if current pricing/usage review supports it. Keep item schema minimal.

## API routes

At minimum:
- `POST /documents/presign`;
- `GET /documents`;
- `GET /documents/{id}`;
- a finalize/confirm route if required by the chosen lifecycle.

Every operation must derive owner from validated JWT context, never from a user-supplied `user_id`.

## IAM

Separate least-privilege permissions:
- document Lambda: only required object prefix operations/presigning capabilities and exact DynamoDB table operations;
- browser gets only presigned operation, no AWS IAM credentials.

## Cost/security gate

If S3/DynamoDB resources were not part of an already approved Gate A envelope, present incremental cost/IAM preview before deployment.

## Tests

- user cannot request another user's key;
- path traversal/arbitrary key impossible;
- invalid extension/size rejected;
- presigned expiration bounded;
- list/get queries are owner-scoped;
- DynamoDB failure sanitized;
- S3 bucket public access tests in template;
- CI has no real S3/DynamoDB calls.

## Acceptance criteria

- Real authenticated user can upload a small approved test document after deployment approval.
- Document is private in S3.
- DynamoDB record belongs to correct Cognito `sub`.
- No document bytes pass through Lambda.
