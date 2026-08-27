# Phase 10 — CI/CD evolution with GitHub OIDC and automated deployment

## Goal

Evolve the CI that has existed since Phase 0 and automate the now-stable deployment process.

## CI

Keep PR CI AWS-free and expand final gates:
- backend lint/format/type/tests;
- frontend lint/type/tests/build;
- SAM validate/build;
- security/isolation tests;
- workflow/IAM/static-credential checks;
- no Bedrock/API live tests.

Configure branch protection recommendation so merge requires CI green.

## CD target

```text
manual merge to main
→ GitHub Actions
→ quality gates
→ GitHub OIDC
→ temporary AWS credentials
→ SAM/CloudFormation backend deploy
→ frontend build + private S3 sync
→ controlled CloudFront invalidation if required
```

The merge remains manual unless the user later asks to automate PR merging at repository policy level. Codex itself may merge its own phase PRs under `AGENTS.md` when no gate is pending.

## OIDC

- Reuse an existing account GitHub OIDC provider if present.
- Create a project-specific deployment role.
- Trust only the actual repository and permitted branch/environment.
- No static AWS keys in GitHub.
- Separate deployment permissions from runtime permissions.

## Bootstrap

Create declarative bootstrap IaC for OIDC deployment access. Avoid circular dependency with the main stack.

## Critical Gate E

Before first automatic AWS deployment from a merge to `main`, stop and show Gate E report.

After approval, CD becomes part of the accepted envelope. Later phase 11 documentation-only merges should not create unnecessary infrastructure changes.

## Deployment safety

- serialize deployments;
- do not cancel CloudFormation mid-deploy by default;
- no Lambda/Bedrock RAG smoke call automatically in pipeline;
- no test document upload automatically;
- empty changeset is success;
- secrets remain outside GitHub;
- frontend build contains only public config.

## Acceptance criteria

- PR CI green without AWS credentials.
- Merge to main deploys the exact tested commit.
- GitHub uses OIDC temporary credentials.
- Backend and frontend deployment succeed.
- No Bedrock query is triggered merely by deployment.
