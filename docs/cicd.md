# CI/CD and GitHub OIDC

PR and main CI run without AWS credentials. The deployment workflow runs only after a push to `main`, repeats all quality gates, then requests a short GitHub OIDC token. Its trust is bound to the immutable repository owner/repository IDs and the main branch.

The manually deployed bootstrap stack is `infrastructure/deployment-access.yaml`. It reuses the account's existing GitHub OIDC provider and separates the GitHub orchestration role from the CloudFormation service execution role.

Required public GitHub repository variables:

- `AWS_ACCOUNT_ID`
- `AWS_REGION`
- `AWS_STACK_NAME`
- `AWS_SAM_ARTIFACT_BUCKET`
- `AWS_DEPLOY_ROLE_ARN`
- `AWS_CLOUDFORMATION_EXECUTION_ROLE_ARN`

No AWS key or application secret is stored in GitHub. The workflow uploads no document and invokes no Bedrock operation.

Recommended `main` ruleset:

- require `backend`, `frontend`, and `infrastructure-and-secrets` PR checks;
- require the branch to be current before merge;
- block force pushes and branch deletion;
- retain administrator recovery rather than applying an unreviewed lockout automatically.

Rollback uses CloudFormation's normal rollback and the previous frontend artifact procedure in `docs/manual-deployment.md`. Disable the deployment workflow or revoke the exact OIDC trust to stop future CD without changing runtime resources.

## Proven deployment

The first end-to-end automatic run completed successfully on 2026-08-27: both `quality` and `deploy` passed for the merged `main` commit, CloudFormation completed, the production frontend was rebuilt from stack outputs, artifacts were published without deletion, and one invalidation was created. Two failures encountered during commissioning—missing SAM transform expansion permission and empty output parsing—were fixed with narrow permissions, explicit output validation, regression tests, and green PR checks.
