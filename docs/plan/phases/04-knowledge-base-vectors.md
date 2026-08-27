# Phase 4 — Bedrock Knowledge Base + S3 Vectors + embeddings

## Goal

Turn uploaded documents into searchable vector data using a managed RAG ingestion path.

## Preferred design

```text
S3 source document + metadata sidecar
→ Bedrock Knowledge Base data source
→ chunking
→ embedding model
→ S3 Vectors vector index
```

Codex must re-verify current AWS support in `eu-west-1` immediately before implementation. If the preferred vector store is no longer supported or becomes economically unsuitable, stop and present alternatives rather than silently switching architecture.

## Knowledge Base

- Managed Bedrock Knowledge Base.
- S3 data source limited to the application document prefix/bucket.
- S3 Vectors preferred vector store.
- Embedding model chosen for multilingual/expected document language and cost; verify current Bedrock model availability and price.
- Start with a simple, documented chunking strategy; do not use expensive advanced parsing unless explicitly approved.

## Ownership metadata

Every source document must have filterable metadata containing at least:
- `owner_sub`;
- `document_id`.

For S3 data sources, use the current supported sidecar metadata mechanism (`<filename>.metadata.json`) or an equally official supported mechanism.

Ownership metadata should normally be filter-only and not included in embeddings unless a documented reason exists.

## Critical Gate B

Before creating the Knowledge Base/vector store or starting the first ingestion, stop and show Gate B report.

Do not rely on a Free Tier assumption for Bedrock/vector operations.

## First validation

After approval:
- ingest one tiny synthetic/non-sensitive document;
- verify ingestion completes;
- perform retrieval-only test if allowed within approved envelope;
- inspect only sanitized result metadata;
- confirm owner/document metadata is present for filtering.

Do not enable generative answer creation yet.

## Tests

Offline tests for:
- metadata sidecar generation;
- ownership field always present;
- Knowledge Base config/IAM assertions;
- chunking config bounded;
- no advanced parser enabled accidentally;
- no OpenSearch Serverless created unless explicitly chosen/approved;
- no generative Bedrock call in this phase.

## Acceptance criteria

- One approved test document can be ingested and retrieved semantically.
- Vector data has ownership metadata.
- Cost model documented.
- CI remains AWS-free.
