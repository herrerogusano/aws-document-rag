# Critical Gates

Codex must keep this file current.

## Gate A — First AWS deployment

Status: `pending`

Before first real AWS deployment, show:
- resources to be created;
- IAM roles/policies;
- region;
- cost review;
- CloudFormation/SAM change preview;
- teardown plan.

## Gate B — First Bedrock Knowledge Base / S3 Vectors / embedding ingestion

Status: `pending`

Before creation or first real ingestion, show:
- chosen embedding model;
- Knowledge Base configuration;
- vector store;
- chunking strategy;
- region support;
- current pricing checked;
- estimated cost for one small test document and expected monthly development usage;
- max document size/count assumptions.

## Gate C — First real generative RAG call

Status: `pending`

Before invoking the generation model on real/synthetic retrieved data, show:
- chosen model/model ID;
- region/inference profile if used;
- current input/output pricing;
- max retrieved chunks;
- max prompt/output tokens;
- estimated single-query cost;
- application retry policy.

## Gate D — Production-like frontend hosting

Status: `pending`

Before creating/activating CloudFront/S3 hosting resources, show resources, security model, current pricing assumptions and teardown.

## Gate E — First automatic CD deployment

Status: `pending`

Before enabling merge-to-main deployment, show:
- OIDC trust scope;
- deployment IAM;
- branch rules;
- what a merge will deploy;
- cost/security consequences;
- rollback behavior.

## Gate F — Destructive operations

Always pending unless specifically approved for the exact action.
