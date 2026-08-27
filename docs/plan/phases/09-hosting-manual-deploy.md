# Phase 9 — Production frontend hosting and stable manual deployment

## Goal

Deploy the complete application in a production-shaped way manually before automating CD.

## Frontend hosting

Preferred:

```text
CloudFront
→ private S3 origin
```

Use Origin Access Control/current recommended AWS pattern. Do not use a publicly readable S3 website bucket.

Custom domain/Route 53/ACM is out of scope unless explicitly requested.

## Auth integration

Update Cognito allowed callback/logout URLs for the deployed frontend origin.

Keep localhost callbacks only if still needed for development.

## API integration

Frontend production build receives non-secret configuration such as:
- API base URL;
- Cognito issuer/client ID/domain;
- region.

No secrets in frontend build.

## Critical Gate D

Before creating/activating frontend hosting, show Gate D report.

## Manual deployment runbook

Document a deterministic manual sequence for:
- backend SAM build/deploy;
- frontend build;
- frontend artifact sync/upload;
- CloudFront invalidation only when needed;
- config checks;
- smoke test.

Do not automate CD yet.

## Smoke test

After approved deployment:
- sign in;
- upload tiny test doc;
- ingest;
- ask one bounded question;
- verify citation;
- inspect sanitized logs.

Do not generate repeated Bedrock test calls.

## Acceptance criteria

- Public frontend URL serves over HTTPS via CloudFront.
- S3 origin remains private.
- Auth callback works.
- Full RAG flow works.
- Manual deployment is documented and repeatable.
- This stability is the prerequisite for Phase 10 CD.
