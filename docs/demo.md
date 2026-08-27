# Repeatable demo runbook

This runbook demonstrates the product without exposing private content or creating repeated model/ingestion cost. Use a dedicated demo user and a synthetic document containing no personal, confidential, or proprietary data.

## Before the call

1. Confirm the hosted shell returns HTTPS 200 and the latest `Deploy` workflow is green.
2. Prepare one UTF-8 TXT file below 10 KiB, for example:

   ```text
   Project Atlas is a fictional migration completed in June 2026.
   Its documented owner is the Platform Enablement team.
   The measured deployment time fell from 40 minutes to 12 minutes.
   ```

3. Sign in once and keep the credentials outside screen sharing, notes, logs, and the repository.
4. Prefer an already indexed copy. Upload and ingest a new copy only when the lifecycle itself must be shown.
5. Set a hard demo budget: at most one ingestion job and one generated question.

## Seven-minute path

1. Open the hosted application and point out HTTPS, the private-origin architecture, and Cognito PKCE sign-in.
2. Sign in. Show that the document list is loaded only after authentication.
3. If demonstrating upload, select the sanitized file. Explain that the browser uploads through a five-minute presigned URL directly to private S3.
4. Show the visible lifecycle: upload, indexing, then `READY`. Do not restart ingestion if it is already running or complete.
5. Select the document scope and ask: `How did deployment time change?`
6. Show that the response is grounded in the synthetic facts and that its citation names the uploaded file.
7. Open the latest GitHub Actions run. Show offline quality gates preceding the OIDC deployment job.
8. In CloudWatch, show only structured status/count fields and 14-day retention. Do not expand tokens, owner IDs, source keys, questions, answers, or document text.

## Expected evidence

- Unauthenticated API access returns `401`; authenticated list/query works.
- The document state reaches `READY` and duplicate ingestion is rejected or idempotent as appropriate.
- A query with evidence returns citations; a question with no evidence produces an insufficient-evidence response without inventing a source.
- The latest main deployment shows `quality` and `deploy` successful.
- Direct unsigned access to the frontend S3 origin is denied while CloudFront serves the shell.

## Safe recovery

- `Failed to fetch`: check browser network/CORS, API URL, and the deployed origin—not document content in logs.
- Session expired: sign in again; the API client performs only one refresh retry.
- Indexing is slow: leave the existing job running and continue with architecture/CI; do not start another.
- No retrieval result: verify the document is `READY` and scope is correct. Do not generate repeated paid queries.
- Deployment issue: follow the rollback section in `docs/manual-deployment.md`; never empty a data bucket as part of a demo.

## After the demo

Record only pass/fail, timestamp, workflow URL, and sanitized counts. Keep the demo document if it will prevent another ingestion; exact deletion of a document, vector, identity, or bucket requires a separately reviewed action.
