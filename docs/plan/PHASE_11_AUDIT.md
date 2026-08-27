# Phase 11 final audit

Audit date: 2026-08-27. Region: `eu-west-1`. No live ingestion, retrieval, generation, document upload, data deletion, or resource deletion was performed for this audit.

## Result

The closeout criteria pass. The authenticated full-stack path was proven incrementally with a real PKCE login, private direct upload, metadata lifecycle, bounded ingestion/retrieval, one cited generation, and production hosting. Offline isolation tests cover distinct owners. Manual and automatic deployments are documented and proven; the latest main deployment is green.

## Verification matrix

| Check | Result |
|---|---|
| Ruff format and lint | Pass |
| mypy strict | Pass |
| Backend pytest | Pass, 53 tests |
| Frontend oxlint | Pass |
| Frontend Vitest | Pass, 6 tests |
| Frontend TypeScript/Vite production build | Pass |
| Main SAM validate/lint and build | Pass |
| Deployment bootstrap SAM validate/lint | Pass |
| Static credential/private-key pattern scan | Pass, no match |
| Production shell | HTTPS 200, HTML, HSTS and CSP present |
| Latest automatic workflow | `quality: success`, `deploy: success` |
| Working tree before closeout commit | Only reviewed Phase 11 documentation changes |

## Deployed resource inventory

The runtime stack reports 33 CloudFormation resources: three Lambda functions, seven Lambda permissions, four IAM roles, two DynamoDB tables, two S3 buckets plus one bucket policy, four CloudFront resources, two API Gateway resources, two Bedrock Knowledge Base/data-source resources, three Cognito resources, two S3 Vectors resources, and one log group. The separate bootstrap stack contains the two deployment roles. Physical IDs, account IDs, user IDs, tokens, and private endpoints are intentionally omitted.

No EC2, ECS/Fargate, RDS, NAT Gateway, OpenSearch Serverless collection, WAF, Route 53 hosted zone, custom ACM certificate, Lambda@Edge, or provisioned database/search capacity exists in this project design.

## IAM review

- Every API route uses the default Cognito JWT authorizer.
- Runtime document/query policies enumerate exact actions and project resource ARNs; the Lambda basic execution policy is the documented log-writing exception.
- The Knowledge Base service role is limited to the embedding model, exact source bucket prefix, and project vector index.
- GitHub OIDC trust is exact immutable repository identity plus `main`; the OIDC role can pass only the CloudFormation execution role.
- The CloudFormation execution role has enumerated control-plane actions and project name/ARN bounds. Services whose control-plane APIs do not support resource-level permissions retain documented wildcard resources inside this service role only.
- The SAM transform expansion permission is limited to `cloudformation:CreateChangeSet` on the regional AWS-owned SAM transform ARN.
- Deployment cannot delete frontend objects and the workflow contains no destructive sync.

## Cost inventory

Variable dimensions are Cognito MAU/email, API requests, Lambda duration/requests, S3 storage/requests, DynamoDB reads/writes/storage, embedding tokens, S3 Vectors storage/query/processing, Nova input/output tokens, CloudWatch logs, CloudFront requests/transfer, and invalidations. Standing high-cost resources were deliberately avoided.

Application bounds remain 20 documents/user, 100 KiB/document, at most five 2,000-character chunks, a 1,000-character question, 256 output tokens, one model attempt, 100 generations/month, API throttling, and 14-day logs. The small portfolio envelope is estimated around cents and roughly below $0.25/month, but AWS pricing, taxes, account-wide usage, abuse, email, and traffic can change the bill. Production should add AWS Budgets/anomaly detection and paid alarms with an approved monitoring budget.

## Cleanup review

No stale TODO/FIXME remains in production source. The mock adapters are intentionally retained because they are dependency-injected only when public Cognito configuration is absent and power credential-free UI tests; configured production selects real API adapters. Historical phase plans remain as audit evidence rather than duplicated operational truth. Stale current-state architecture/development/README content was replaced.

No data-bearing cleanup was authorized or necessary. Gate F remains required before deleting any named document object, vector index, identity, bucket, table, distribution, stack, or other AWS resource.

## Known limitations

This is a one-Region, low-volume portfolio system with tiny documents, fixed chunking, polling, a generated domain, and application-level tenant isolation in shared resources. It has no malware scanning, data-subject deletion workflow, WAF, custom domain, multi-Region recovery, browser end-to-end CI, evaluation dashboard, or production alerting. Those are explicit future decisions, not hidden completion claims.
