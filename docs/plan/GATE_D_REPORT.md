# Gate D report — production-like frontend hosting

Prepared 2026-08-27 from current AWS CloudFront and S3 documentation/pricing.

## Exact resources

- one encrypted S3 frontend artifact bucket with all Block Public Access controls enabled and no website endpoint;
- one CloudFront Origin Access Control (OAC) configured to always sign S3 origin requests with SigV4;
- one CloudFront distribution using the default CloudFront HTTPS certificate, HTTP-to-HTTPS redirect, TLS 1.2 minimum, HTTP/2+3, Price Class 100 and SPA error routing;
- one source-ARN-bound bucket policy granting only `s3:GetObject` to that distribution;
- one cache policy and one response-headers policy with HSTS, frame denial, content-type protection, referrer policy and a bounded CSP;
- Cognito callback/logout and API/document-upload CORS extended to the exact generated CloudFront origin while retaining localhost for development.

No custom domain, Route 53 zone, ACM certificate, WAF, Lambda@Edge, CloudFront Functions or public S3 website is created.

## Security model

Viewers use HTTPS through CloudFront. CloudFront alone reads the private S3 origin through OAC; the bucket policy is conditioned on the exact distribution ARN. Static files contain only public SPA configuration (API URL, Cognito domain/client ID and redirect URL), never credentials or tokens. API and document access remain JWT/owner protected; hosting the shell publicly does not weaken backend authorization.

## Current pricing assumption

The production bundle is about 0.2 MiB compressed and anticipated portfolio traffic is below 1,000 requests/10 MiB per month. S3 Standard in Ireland was listed at $0.023/GB-month plus request charges. CloudFront's current pricing includes a $0/month Free plan with 1M requests and 100 GB transfer, while pay-as-you-go also has substantial free usage allowances. The first 1,000 invalidation paths/account/month are currently free.

The expected bounded hosting cost is below $0.01/month even without relying on a frontend bundle storage allowance; transfer/request cost depends on account eligibility and actual traffic. A single `/*` invalidation counts as one path. No minimum hourly/provisioned resource is introduced.

Official references:

- [CloudFront pricing](https://aws.amazon.com/cloudfront/pricing/)
- [S3 pricing](https://aws.amazon.com/s3/pricing/)
- [Restrict an S3 origin with OAC](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html)
- [CloudFront invalidation pricing](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/PayingForInvalidation.html)

## Deployment and teardown

CloudFormation creates the empty hosting resources first. The production frontend is built with public stack outputs, uploaded with long cache headers for hashed assets and no-cache for `index.html`, then one invalidation is submitted. Smoke checks verify HTTPS, private-origin denial and Cognito redirect configuration.

Teardown is deliberately not automatic. Exact order: disable then delete the distribution, remove the bucket policy/OAC, empty only the named frontend artifact bucket, and delete that bucket/cache/headers resources through CloudFormation. Backend documents, vectors, metadata, identities and Knowledge Base remain untouched.

## Authorization

The user explicitly delegated autonomous approval of successive bounded gates on 2026-08-27. Gate D is approved only for the resources, security model and cost envelope above. Gate E remains separate.

## Deployment result

CloudFormation reached `UPDATE_COMPLETE` and CloudFront reached `Deployed`. The production shell returned HTTPS 200 with the configured security headers; an unsigned direct S3 request returned 403; all four frontend-bucket public-access controls were enabled; Cognito callback/logout and API CORS contained the exact CloudFront origin. One frontend publish and one wildcard invalidation completed without deleting any object. No document ingestion or Bedrock model call was triggered.
