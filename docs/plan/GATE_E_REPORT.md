# Gate E report — first automatic deployment from GitHub Actions

Prepared 2026-08-27 using the current GitHub Actions OIDC subject format and official AWS/GitHub guidance.

## OIDC trust scope

The account already has the GitHub OIDC provider. A new project deployment role trusts only:

- audience `sts.amazonaws.com`;
- the immutable default subject prefix for the actual repository owner ID and repository ID;
- `ref:refs/heads/main` exactly.

The role cannot be assumed by pull requests, forks, tags, other branches, renamed/recycled repositories or other owners. GitHub exposes no AWS access key; `id-token: write` is granted only to the deployment job and exchanged for a short STS session.

## Deployment IAM

The bootstrap stack creates two separate roles:

1. GitHub deploy role — create/inspect/execute change sets only for `aws-document-rag-dev`, pass only the project CloudFormation execution role, read/write the existing SAM artifact bucket and private frontend artifact bucket without delete permission, and invalidate only the exact CloudFront distribution.
2. CloudFormation execution role — trusted only by CloudFormation and limited to the named/prefixed project resources and enumerated service control-plane operations needed by this SAM stack. It is separate from all runtime roles and does not have `AdministratorAccess`.

Some control-plane APIs do not support fine-grained resource ARNs. Their wildcard resources are isolated in the CloudFormation execution role, enumerated by action/service and documented in the bootstrap template; the OIDC role itself stays bound to the exact stack, buckets, distribution and pass-role target.

## Branch and workflow rules

- event: push to `main` only; documentation-only changes are ignored;
- checkout uses the exact merged commit;
- full offline backend/frontend/SAM gates run before AWS credentials are requested;
- concurrency group serializes deployment and `cancel-in-progress: false` avoids interrupting CloudFormation;
- GitHub environment/secrets are not required; only public repository variables hold role ARNs, account/region, bucket and stack names;
- recommended repository rule: require the three PR CI jobs before merge and block force pushes/deletion on `main`. It is documented but not enabled automatically because it changes repository governance.

## What a merge deploys

After quality gates, the workflow assumes the temporary role, builds SAM, deploys the exact commit with rollback enabled and empty changesets treated as success, reads public stack outputs, builds the SPA, uploads immutable hashed assets plus no-cache `index.html` without deleting old objects, and creates one `/*` invalidation.

It never uploads a test document, starts ingestion, calls Knowledge Base retrieval, invokes a model, reads document data or runs live RAG tests.

## Cost and security consequences

OIDC, IAM roles and CloudFormation change sets have no standing charge. Ordinary deployment adds S3 artifact requests/storage and one invalidation path; current CloudFront policy includes the first 1,000 invalidation paths/account/month free. The deployed application remains within Gate B/C/D limits. Temporary credentials expire after 30 minutes and the action validates the expected account ID.

## Rollback

CloudFormation rollback remains enabled. A failed frontend publish stops before invalidation; prior hashed assets remain and `index.html` can be restored with the manual runbook. The workflow never empties buckets or deletes data. Disable CD by disabling/removing the workflow or revoking the exact role trust; neither action affects runtime resources.

Official references:

- [GitHub OIDC with AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)
- [Immutable OIDC subject format](https://github.blog/changelog/2026-04-23-immutable-subject-claims-for-github-actions-oidc-tokens/)
- [AWS IAM OIDC role guidance](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html)
- [AWS credentials action](https://github.com/aws-actions/configure-aws-credentials)

## Authorization

The user explicitly delegated autonomous approval of successive bounded gates on 2026-08-27. Gate E is approved only for this trust, IAM, branch, workflow and rollback envelope. Gate F remains exact-action-only.
