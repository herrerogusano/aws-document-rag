# Phase 8 security, reliability, observability and cost audit

Audit date: 2026-08-27. Region: `eu-west-1`.

## Result

No unexplained critical finding remains in the reviewed design. The live pre-hardening audit confirmed that all seven HTTP routes used JWT authorization, CORS allowed only `http://localhost:5173`, the document bucket had all four Block Public Access controls enabled and no public bucket policy, and DynamoDB used on-demand billing.

The hardening change closes the material gaps found during that audit:

- all application logs use an allow-listed structured schema with correlation ID, result counts and status only; questions, document text, tokens, presigned URLs, owner IDs and S3 keys are excluded;
- API access logs include only request ID, route, status and response length and expire after 14 days;
- AWS SDK connect/read timeouts are explicit; model invocation has one total attempt so an SDK retry cannot duplicate generation;
- API traffic is throttled to 5 requests/second with burst 10;
- a conditional DynamoDB counter enforces the approved 100-generation-call monthly development ceiling before model invocation;
- uploads and ingestion now share the same 100 KiB maximum and each owner is limited to 20 documents;
- repeated finalize calls cannot regress `INGESTING` or `READY` state;
- document Lambda permissions were reduced to the exact S3 and DynamoDB operations used; query Lambda has only document `GetItem`, budget `UpdateItem`, Knowledge Base `Retrieve`, and the approved model ARNs.

The Lambda basic execution role necessarily retains AWS-managed CloudWatch Logs permissions, including log-group creation. This is the only reviewed runtime wildcard-resource exception and does not grant access to document, identity, vector or model data.

## Invariant checklist

| Area | Evidence / control | Result |
|---|---|---|
| S3 privacy | SSE-S3, four Block Public Access flags, no public policy | Pass |
| JWT coverage | API default Cognito JWT authorizer; no route opts out | Pass |
| Browser origins | exact parameterized origin; authorization/content-type headers only | Pass |
| Upload | server-generated owner prefix, allowed extensions, 100 KiB, 300-second PUT | Pass |
| Metadata | owner is JWT `sub`; owner + document ID DynamoDB key | Pass |
| Retrieval | mandatory exact `owner_sub`; optional document filter only narrows | Pass |
| Generation | five chunks, 2,000 chars/chunk, 1,000-char question, 256 output tokens, one attempt | Pass |
| Prompt injection | retrieved text serialized and declared untrusted under system policy | Pass |
| Errors | public errors are stable and sanitized | Pass |
| Logs | content-free structured allow list; 14-day API retention | Pass |
| State transitions | duplicate ingest conflict; finalize cannot regress later states | Pass |
| Cost ceiling | 20 documents, 100 KiB each, 200 retrievals and 100 generations/month | Pass |

## Current cost inventory

Rates below were checked against the AWS Price List API and official pricing pages on 2026-08-27. They are estimates, not a billing guarantee, and do not assume Free Tier for the upper bound.

| Service | Current charge dimension / checked rate | Bounded development estimate |
|---|---|---|
| Cognito | Essentials tier listed at $0.015/MAU in `eu-west-1`, subject to its current MAU allowance | one active user: at most $0.015 before allowance |
| API Gateway HTTP API | $1.11/million for the first 300M Ireland requests | 2,000 requests: about $0.0022 |
| Lambda | requests plus Arm duration in GB-seconds | a few thousand short invocations: below $0.01 |
| S3 documents | $0.023/GB-month Standard; $0.005/1,000 PUT/LIST plus GET charges | 2 MiB maximum source corpus plus sidecars: below $0.01 |
| DynamoDB | $0.705/million WRUs, $0.1415/million RRUs, $0.283/GB-month beyond storage allowance | document metadata + one monthly counter: below $0.01 |
| Titan Text Embeddings V2 | $0.000026004/1K input tokens | 20 tiny documents: expected below $0.02 |
| Bedrock Knowledge Bases | no provisioned collection in this design; ingestion/retrieval uses model, S3 and vector dimensions | covered by embeddings and S3 Vectors |
| S3 Vectors | $0.06/GB-month storage; $2.50/million queries; processing/PUT dimensions also apply | tiny index + 200 retrievals: expected below $0.01 |
| Nova Lite | $0.000069/1K input and $0.000276/1K output tokens (Price List API, 2026-08-28) | approved 100-query envelope remains below $0.10 |
| CloudWatch | $0.57/GB Standard log ingestion and $0.03/GB-month storage in Ireland | concise logs + 14-day API retention: expected below $0.01 |
| Frontend hosting | Added in Phase 9: private S3 artifact bucket plus CloudFront OAC distribution, Price Class 100 | Expected below $0.01/month at the documented portfolio traffic; see Gate D |

Expected bounded application plus hosting usage remains roughly below $0.25/month before account-level taxes, pricing changes, unusual traffic, Cognito email delivery, or unrelated workloads. This is an estimate rather than a billing guarantee.

Official sources:

- [Cognito pricing](https://aws.amazon.com/cognito/pricing/)
- [API Gateway pricing](https://aws.amazon.com/api-gateway/pricing/)
- [Lambda pricing](https://aws.amazon.com/lambda/pricing/)
- [S3 and S3 Vectors pricing](https://aws.amazon.com/s3/pricing/)
- [DynamoDB pricing](https://aws.amazon.com/dynamodb/pricing/)
- [Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)
- [CloudWatch pricing](https://aws.amazon.com/cloudwatch/pricing/)
- [CloudFront pricing for the later hosting gate](https://aws.amazon.com/cloudfront/pricing/)

## Deferred deliberately

- No paid CloudWatch alarm is added. A standard alarm is currently $0.10 per metric-month in Ireland, disproportionate to this bounded portfolio environment. Native Lambda/API metrics and structured logs remain available. Production should add 5xx, throttling and generation-budget alarms with an explicit monitoring budget.
- No WAF, custom domain, multi-Region replication, provisioned throughput, OpenSearch Serverless, reranker or advanced parser is enabled.
- The Phase 9/10 hosting and deployment gates were completed later; no WAF/custom domain/multi-Region/provisioned search resources were added.

## Operational checks

After deployment, verify the transformed roles contain no wildcard action, all routes remain JWT-protected, QueryFunction reports a 30-second timeout and JSON logging, the API log group retains 14 days, and a content-free test query log contains correlation/count fields only.

The first deployment attempt tried to reserve two QueryFunction concurrency units, but this account's concurrency quota would have reduced unreserved concurrency below Lambda's mandatory minimum of ten. CloudFormation rolled back cleanly. The reservation was removed; API throttling and the atomic monthly counter remain the effective cost controls without requesting a quota increase.

Post-deployment verification passed: the stack reached `UPDATE_COMPLETE`; all routes remained JWT-protected; every Lambda reported JSON logging and 14-day retention; QueryFunction reported a 30-second timeout; the API access log retained 14 days; reviewed application/Knowledge Base inline roles had neither wildcard actions nor wildcard resources. A malformed synthetic request produced the expected structured `query_rejected` event and a CloudWatch search found zero copies of its sentinel private-content string.
