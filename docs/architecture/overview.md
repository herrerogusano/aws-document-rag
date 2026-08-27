# Architecture overview

The application is a single-Region, serverless, owner-isolated RAG system. `template.yaml` is the runtime source of truth; `infrastructure/deployment-access.yaml` separately bootstraps deployment trust.

## Runtime boundaries

- CloudFront serves the React SPA from a private OAC-protected S3 origin.
- Cognito handles Authorization Code + PKCE for a public SPA client.
- API Gateway validates JWTs before invoking three Lambdas: identity, documents, and query.
- The document Lambda manages five-minute direct-to-S3 uploads, DynamoDB lifecycle records, metadata sidecars, and Bedrock Knowledge Base ingestion.
- The query Lambda retrieves through the Knowledge Base with a mandatory JWT-derived `owner_sub` filter, validates returned metadata, consumes one atomic budget unit, and invokes Nova Lite once.
- The Knowledge Base chunks source objects, produces Titan Text Embeddings V2 vectors, and indexes them in S3 Vectors.

## Authoritative versus derived state

| State | Authority | Recovery principle |
|---|---|---|
| Identity and stable owner `sub` | Cognito | Never accept owner from the browser |
| Source bytes and metadata sidecar | Private document S3 | Treat as private data; no automatic teardown |
| Lifecycle, filenames, job IDs, usage counter | DynamoDB | Conditional updates enforce transitions/budgets |
| Chunks and embeddings | Knowledge Base + S3 Vectors | Derived from the source/sidecar; re-index deliberately |
| Frontend artifact | Private frontend S3 | Hashed assets immutable; shell no-cache and recoverable |

## Isolation invariants

1. API Gateway authenticates every route.
2. Lambda derives owner from the verified JWT `sub`.
3. Object keys and DynamoDB reads include that owner.
4. Server-generated sidecars carry the same owner and document ID.
5. Every retrieval contains the exact owner filter; optional document scope can only narrow it.
6. Returned metadata is rechecked before passage text enters the prompt.
7. Model output cites only the accepted retrieval set.

## Deployment boundary

PR CI has no AWS credentials. Main CD receives a short OIDC session only after all quality gates pass. The GitHub deploy role can orchestrate one stack, upload artifacts without deletion, pass only the project CloudFormation execution role, and invalidate one distribution. The CloudFormation role manages enumerated project resources; runtime roles remain separate and least-privilege.

See the diagrams and service rationale in the root `README.md`, the security/cost evidence in `docs/plan/PHASE_08_AUDIT.md`, and the deployment trust report in `docs/plan/GATE_E_REPORT.md`.
