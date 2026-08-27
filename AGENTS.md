# Codex Operating Policy — AWS Document RAG

This file defines the permanent autonomous workflow for this repository.

## Mission

Advance the project phase by phase without requiring routine user supervision. Ask the user only at explicitly defined critical gates or when progress is impossible because required credentials/connections are unavailable.

## Source of truth

Read in this order before every phase:

1. `AGENTS.md`
2. `PLAN.md`
3. `docs/plan/PROGRESS.md`
4. `docs/plan/GATES.md`
5. current file under `docs/plan/phases/`
6. repository code and current docs

Never assume documentation is more accurate than the actual code/deployed state. Reconcile discrepancies.

## Branch / commit / PR autonomy

For every phase:

- Start from current `main`.
- Create `phase/<NN>-<short-name>`.
- Commit autonomously when the phase is coherent and tests pass.
- Push autonomously.
- Create the PR autonomously using GitHub CLI/API when authenticated.
- Include summary, tests, AWS/IAM changes, cost impact and known limitations.
- Wait/check CI.
- Fix CI failures autonomously when they are within phase scope.
- Merge autonomously when all acceptance criteria pass and no gate is pending.
- Prefer squash merge unless repository conventions say otherwise.
- Delete merged remote/local phase branches when safe.

Do not ask permission for routine branch creation, commits, pushes, PR creation or merges.

## Critical gates — MUST stop and ask

Stop before performing any of these actions unless the user has already explicitly approved the exact bounded change:

1. First creation or activation of an AWS resource/service with material, recurring, potentially billable or unknown cost.
2. First real Bedrock embedding, ingestion, retrieval+generation or other intentional model invocation when pricing has not yet been approved for this project.
3. Increasing an already approved cost envelope, model, token limit, ingestion frequency, vector capacity or deployment frequency materially.
4. Creating/changing IAM trust or permissions that broaden access materially, include sensitive data access, or require wildcard permissions not already approved.
5. Creating/managing secrets, passwords or user credentials when user interaction is required.
6. Destructive operations: deleting production-like AWS resources/data, replacing buckets/tables/user pools, destroying stacks, deleting vector indexes or knowledge bases with data.
7. Schema/data migrations with meaningful risk of data loss.
8. Enabling public access to S3 or weakening auth/CORS/security controls.
9. Changing region from `eu-west-1` for deployed resources.
10. Enabling CD to deploy automatically to AWS for the first time.
11. Any action the repository's current `GATES.md` explicitly marks as pending.

## Actions that are NOT critical gates

Proceed autonomously with:

- local code changes;
- local tests/mocks/fixtures;
- CI workflow improvements that do not obtain AWS credentials;
- documentation;
- branch/commit/push/PR/merge when no critical gate is crossed;
- SAM build/validate locally;
- formatting/lint/type checking;
- refactors within current architecture;
- adding mocked tests;
- updating application code after an AWS architecture/cost envelope has already been approved, provided it does not broaden that envelope.

## Cost policy

Before any gated AWS creation/activation, produce a short gate report:

- resources/actions;
- current official pricing source checked and date;
- expected usage pattern;
- expected monthly/request cost range where calculable;
- Free Tier assumptions, if any, clearly marked as assumptions rather than guarantees;
- maximum bounded model calls / uploads / retrievals when relevant;
- rollback/disable plan.

Never claim a service is free merely because expected usage is low.

## Security

- No static AWS access keys in GitHub.
- No secrets in `.env` committed to Git.
- Do not log Cognito tokens, presigned URLs, S3 object contents, Bedrock prompts containing document text, or user documents.
- Treat JWT claims as untrusted until validated by API Gateway/known auth path.
- Use Cognito `sub` as the stable application owner identifier, not email.
- Every document access/query must be scoped to authenticated owner.
- Presigned upload keys must be server-generated and owner-scoped.
- S3 buckets remain private.
- Runtime roles follow least privilege.

## RAG isolation invariant

The system must never retrieve another user's document through the RAG path.

Every indexed document must include filterable ownership metadata and every user query must apply the authenticated user's owner filter at retrieval time.

Tests must fail if retrieval is possible without the owner filter.

## CI evolution

CI exists from Phase 0 and grows with the project. A new phase should extend CI when it introduces a new testable concern.

PR CI must never require real AWS credentials and must never invoke Bedrock.

## CD rule

Until Phase 10 is explicitly approved and completed, deployments remain manual/gated. After CD is enabled, merges to `main` may deploy automatically only within the approved architecture/cost/security envelope.

If a phase PR would cause CD to create a new gated resource or broaden cost/security, stop before merging the PR.

## Failure handling

If a tool/command fails:

1. diagnose;
2. retry only when safe and justified;
3. fix autonomously when within scope;
4. do not bypass security/cost checks to make progress;
5. stop only when a critical gate or unavailable required credential blocks progress.
