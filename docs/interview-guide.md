# Interview guide

Use the 20-second answer first, expand to the two-minute answer when invited, and use the deep notes for follow-ups.

## What is RAG, and why embeddings/vector search?

**20 seconds.** RAG retrieves relevant private passages before generation, so the model answers from supplied evidence and can cite it. Embeddings turn semantically similar text into nearby vectors, allowing retrieval by meaning instead of exact words.

**Two minutes.** Ingestion chunks each owner-tagged document, creates Titan embeddings, and stores them in S3 Vectors. At query time the Knowledge Base embeds the question, applies an exact owner metadata filter, and returns the nearest passages. The Lambda validates metadata again, bounds the context, and gives it to Nova Lite as untrusted evidence. This is cheaper and more focused than sending a whole PDF, avoids model context limits, and makes citations possible. It still does not guarantee truth: retrieval quality, source quality, and generation behavior all need evaluation.

**Deep technical.** Cosine similarity compares vector direction; the index dimension must match the embedding model (1,024 here). Fixed chunks use 300 tokens with 20% overlap. Retrieval is capped at five results, then application checks defend against filter/configuration mistakes. A production evaluation would measure recall@k, citation precision, answer faithfulness, latency, and cost on a versioned question set.

## What is a vector store, and why S3 Vectors instead of S3 or OpenSearch?

**20 seconds.** Ordinary S3 stores source bytes and metadata sidecars; S3 Vectors stores embeddings in an index that supports similarity queries. It fits this tiny, serverless workload without a provisioned search cluster.

**Two minutes.** S3 is durable object storage but cannot natively answer nearest-neighbor queries over embeddings. S3 Vectors provides that retrieval primitive and integrates with Bedrock Knowledge Bases. OpenSearch would offer richer hybrid search, tuning, and analytics, but a provisioned collection would be unnecessary cost and operational surface for a bounded portfolio corpus.

**Deep technical.** The vector index uses the Titan V2 dimension and cosine distance. Source documents remain authoritative in private S3; vector entries are derived data. The tradeoff is less search customization than OpenSearch. At larger scale or with hybrid lexical/semantic ranking requirements, benchmark the alternatives rather than assuming one store wins.

## What does Bedrock Knowledge Bases manage?

**20 seconds.** It connects the S3 data source, parsing/chunking, Titan embeddings, S3 vector index, ingestion jobs, metadata filters, retrieval, and source attribution.

**Two minutes.** Without it, the application would need its own extraction pipeline, chunk IDs, embedding batches, vector writes, synchronization, retrieval client, and citation mapping. The managed path reduces code and keeps the demo focused on isolation and product behavior. Lambda still owns authorization, lifecycle policy, budgets, result validation, prompt construction, and public error handling.

**Deep technical.** The data source consumes a metadata sidecar so `owner_sub` and `document_id` become filterable attributes. Knowledge Bases is not the authorization boundary: the application must always build the exact filter from the JWT and reject mismatched returned metadata.

## Why DynamoDB when vectors live elsewhere?

**20 seconds.** Vectors answer semantic similarity; DynamoDB is the authoritative transactional record for owner, filename, status, object key, ingestion job, and monthly usage.

**Two minutes.** The UI needs strongly defined lifecycle transitions and owner-scoped listing that a vector index should not provide. A composite owner/document key supports exact reads and owner queries. Conditional updates prevent duplicate ingestion and an atomic counter prevents exceeding the generation ceiling.

**Deep technical.** Treat vector records as derived indexes and DynamoDB as control-plane state. Conditional expressions implement optimistic state transitions. On-demand billing fits unpredictable low traffic; high predictable traffic could justify provisioned capacity and autoscaling.

## Why presigned URLs?

**20 seconds.** Lambda authorizes the operation and returns a five-minute PUT capability, then the browser uploads directly to private S3. Document bytes do not traverse API Gateway or Lambda.

**Two minutes.** The server generates the owner-prefixed key and constrains extension, content type, and size before signing. This reduces latency, payload limits, Lambda duration, and cost. The URL is a temporary bearer capability, so it must never be logged or exposed. Finalization confirms the object before metadata advances.

**Deep technical.** Presigning does not make the bucket public. Bucket policy/IAM still control what can be signed, while CORS controls browser permission but is not authorization. Production hardening could add checksum enforcement and an asynchronous malware/content scan before ingestion.

## Cognito User Pool, PKCE, JWT, and API authorizer

**20 seconds.** Cognito authenticates the user through Authorization Code + PKCE; the public SPA has no client secret. API Gateway validates issuer, audience, signature, and expiry, then Lambda derives the owner from the verified `sub` claim.

**Two minutes.** PKCE binds the authorization request to a one-time verifier, protecting a public client that cannot safely hold a secret. The SPA sends the access token as a bearer token. API Gateway's JWT authorizer rejects invalid or missing tokens before Lambda. Every route uses the default authorizer. Lambda never trusts an owner ID from request JSON.

**Deep technical.** Authentication proves token validity; authorization is still application logic. `sub` is stable within the user pool and is used in object prefixes, DynamoDB keys, and Knowledge Base filters. Tokens live in browser session storage in this implementation; stronger production threat models may choose a BFF with secure HttpOnly cookies.

## How is tenant isolation guaranteed?

**20 seconds.** Defense in depth: JWT-derived owner, owner-prefixed S3 keys, owner/document DynamoDB keys, mandatory retrieval filters, post-retrieval metadata validation, and IAM that exposes no cross-owner listing API.

**Two minutes.** The client cannot select another owner. List/read/update operations all include the verified `sub`; upload keys are server-generated; sidecar metadata is server-owned; queries cannot be built without the exact owner filter. Tests use two owners and prove one cannot retrieve the other's document. Result validation catches an upstream filtering mistake before context reaches the model.

**Deep technical.** It is application-level multi-tenancy within shared resources, not separate accounts or KMS keys per tenant. Higher-assurance isolation could use tenant roles, separate buckets/tables/knowledge bases, policy conditions, or accounts, at higher cost and operational complexity.

## Prompt injection in RAG

**20 seconds.** A document can contain instructions that try to override the application. Retrieved text is labeled untrusted, serialized as data, bounded, and never allowed to request secrets or change authorization.

**Two minutes.** RAG sources are not inherently trustworthy. The system prompt separates policy from retrieved passages and tells the model to answer only from evidence. The application excludes secrets from context/logs and validates owner metadata before generation. Citations make the evidence inspectable. These controls reduce risk but cannot mathematically eliminate model manipulation.

**Deep technical.** Production defense adds document trust labels, sanitization, model/tool permission separation, adversarial evaluation, output policy checks, and human review for high-impact actions. This application gives the model no tools and no capability to alter infrastructure or data.

## Why Lambda rather than EC2 or Fargate?

**20 seconds.** Requests are short, bursty, and low volume, so Lambda removes idle-server cost and operations. The workload fits its execution and payload limits because uploads go directly to S3.

**Two minutes.** API handlers perform metadata calls, ingestion control, retrieval, and one bounded model request. There is no long-running process or local state. EC2 would require patching/scaling; Fargate would help for long-running containers or sustained throughput but adds service and idle-task overhead.

**Deep technical.** Cold starts, duration limits, concurrency quotas, and connection reuse are Lambda tradeoffs. Ingestion itself is managed by Bedrock, so it does not occupy Lambda. A heavy parser, streaming job, or long evaluation batch could move to Step Functions/ECS while retaining this API boundary.

## SAM, CloudFormation, and Terraform

**20 seconds.** CloudFormation is the AWS deployment engine; SAM is its serverless shorthand and local build tooling. Terraform is a multi-provider alternative with a separate state model.

**Two minutes.** SAM expands functions, APIs, permissions, and deployment artifacts into CloudFormation, which provides change sets and rollback. It suits an AWS-only serverless project and keeps one native stack. Terraform would be reasonable for multi-cloud/provider integrations or an organization already standardized on its workflows.

**Deep technical.** The CI role creates a change set for one stack and passes a separate CloudFormation execution role. The execution role needs a narrowly scoped permission to expand the SAM transform. Bootstrap IAM is deployed separately because the pipeline cannot safely create its own initial trust.

## CI versus CD, GitHub OIDC, and bootstrap

**20 seconds.** CI began offline to validate every phase safely. CD was added only after manual deployment was repeatable. GitHub exchanges an OIDC token for a short AWS session, so no static AWS key exists in GitHub.

**Two minutes.** PR jobs run Python, frontend, SAM, and secret-pattern gates without AWS access. On merged `main`, the workflow repeats those gates, obtains OIDC only in the deploy job, updates the exact stack with rollback, builds from public outputs, publishes without deletion, and invalidates once. Trust is bound to immutable repository identity plus `main`.

**Deep technical.** The bootstrap stack creates an orchestration role and a CloudFormation service role. `iam:PassRole` is limited to that target and service. Concurrency serializes deployments. The workflow deliberately avoids live RAG tests, keeping deployments deterministic and preventing surprise model/ingestion charges.

## Where can this architecture cost money?

**20 seconds.** Main dimensions are model input/output tokens, embeddings, vector operations/storage, requests/duration, S3/DynamoDB/log storage, CloudFront traffic, and Cognito active users.

**Two minutes.** The project bounds the expensive paths: 100 KiB and 20 documents per user, five retrieved chunks, 256 output tokens, one model attempt, 100 generations/month, throttling, concise 14-day logs, on-demand tables, and no provisioned search cluster. Small demo usage is expected around cents, but pricing and account-wide usage must still be monitored.

**Deep technical.** Ingestion cost scales with parsed tokens and re-indexing; query cost scales with retrieval/vector work and generated tokens. Logs and abusive traffic can become indirect multipliers. A production version should combine application counters with AWS Budgets, anomaly detection, alarms, per-tenant quotas, and explicit retention/deletion policies.
