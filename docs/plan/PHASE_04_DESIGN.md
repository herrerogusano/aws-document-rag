# Phase 4 design — Bedrock Knowledge Base with S3 Vectors

Prepared on 2026-08-27. This document is configuration design only; no Bedrock or S3 Vectors resource has been created and no model has been invoked.

## Bounded development configuration

- Region: `eu-west-1` only.
- Embedding model: Amazon Titan Text Embeddings V2, model ID `amazon.titan-embed-text-v2:0`.
- Vector size: 1,024 dimensions for the first quality baseline.
- Vector store: one S3 vector bucket and one vector index; no OpenSearch Serverless collection.
- Source: the existing private document S3 bucket, restricted to `users/`.
- Chunking: fixed size, 300 tokens with 20% overlap; no semantic, hierarchical, advanced or foundation-model parser.
- Ownership metadata: adjacent `<source>.metadata.json` sidecar with filter-only `owner_sub` and `document_id` string attributes.
- First validation: at most one tiny non-sensitive TXT document, one ingestion job and one retrieval-only query with an exact `owner_sub` filter. No generation call.

## Isolation invariant

All retrieval code must require an authenticated Cognito `sub` and construct an equality filter on `owner_sub`. The retrieval adapter will not expose an unfiltered execution path. Offline tests must fail if the filter is absent.

## IAM outline for Gate B

- Bedrock Knowledge Base service role trusted only by `bedrock.amazonaws.com`, with source-account/source-ARN conditions where supported.
- Read-only access to the existing source bucket `users/*` objects and their sidecars.
- Use of only the selected Titan embedding model in `eu-west-1`.
- Access to only the new S3 vector bucket/index.
- Application ingestion role limited to starting and reading ingestion jobs for the exact knowledge base/data source.

The exact CloudFormation policy and change set will be prepared and reviewed before deployment. No wildcard resource permission will be accepted silently.

## Gate boundary

Gate B remains pending. Creating the Knowledge Base, S3 vector bucket/index, service role, data source, sidecars in S3, or invoking embedding/ingestion/retrieval is prohibited until the bounded Gate B report is approved.
