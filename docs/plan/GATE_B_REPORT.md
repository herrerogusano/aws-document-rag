# Gate B report — first Bedrock Knowledge Base / S3 Vectors ingestion

Prepared 2026-08-27 from current AWS documentation and the AWS Price List API for `eu-west-1`. Status: **pending user approval**.

## Exact bounded change

- Create one Amazon Bedrock Knowledge Base, one S3 data source, one S3 vector bucket and one 1,024-dimension vector index in `eu-west-1`.
- Create one least-privilege Bedrock service role scoped to the existing source bucket, the selected embedding model and the exact vector bucket/index.
- Use Amazon Titan Text Embeddings V2 (`amazon.titan-embed-text-v2:0`).
- Use fixed-size 300-token chunks with 20% overlap and the standard parser. No semantic/hierarchical chunking and no advanced parser.
- Add filter-only `owner_sub` and `document_id` metadata sidecars adjacent to source objects.
- First run: one non-sensitive TXT document no larger than 10 KiB, one ingestion job and one retrieval-only query with an exact owner filter. No generative model call.

## Region and support

AWS currently lists managed Knowledge Bases, Titan Text Embeddings V2 and S3 Vectors in Europe (Ireland), `eu-west-1`. The S3 Vectors integration supports filterable custom metadata; its Knowledge Base limit is 1 KiB and 35 metadata keys per vector. This design uses two short string keys.

Official references:

- [Bedrock Knowledge Base supported Regions](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-regions.html)
- [Knowledge Base embedding models and Regions](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-supported.html)
- [S3 Vectors Regions and quotas](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-regions-quotas.html)
- [Using S3 Vectors with Bedrock Knowledge Bases](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-bedrock-kb.html)
- [S3 metadata sidecars](https://docs.aws.amazon.com/bedrock/latest/userguide/s3-data-source-connector.html)

## Current price basis

The AWS Price List API returned these on-demand `eu-west-1` rates on 2026-08-27:

- Titan Text Embeddings V2 input: **$0.000026004 per 1,000 tokens**.
- S3 Vectors storage: **$0.06 per GB-month**.
- S3 Vectors writes: **$0.20 per GB written**.
- S3 Vectors ordinary API requests: **$0.055 per 1,000 requests**; query API requests: **$0.0025 per 1,000 queries**.
- Query processing: starts at **$0.000003906 per GB processed** for the first tier; returned data is **$0.01 per GB**, subject to the pricing-page per-query allowance.

Pricing references:

- [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)
- [Amazon S3 and S3 Vectors pricing](https://aws.amazon.com/s3/pricing/)

No Free Tier credit is assumed.

## Estimated bounded cost

- First 10 KiB test document: embedding cost is below **$0.001** even under a deliberately pessimistic character-to-token assumption; vector storage/write and one retrieval are fractions of a cent. Expected total is **below $0.01**.
- Monthly development ceiling for this approval: at most 20 documents, each at most 100 KiB; at most 20 ingestion jobs and 200 retrieval-only queries. The calculated embedding/vector portion is expected below **$0.10/month** under pessimistic token and chunk assumptions. Existing S3, Lambda, API Gateway and DynamoDB request/storage charges remain additional but negligible at this volume.
- This approval would not cover files above 100 KiB for ingestion, more than 20 documents/month, more than 200 retrievals/month, semantic/advanced parsing, reranking, generation, OpenSearch Serverless, provisioned throughput or a region change.

## Security and rollback

- Retrieval must always include `owner_sub == authenticated Cognito sub`; no unfiltered adapter method will exist.
- The service role will read only the source bucket's `users/*` objects/sidecars, invoke only the selected embedding model and access only the exact vector resources.
- S3 source and vector storage remain private and encrypted with AWS-managed server-side encryption.
- Rollback/disable: stop ingestion, detach/disable the data source and remove the new Knowledge Base/vector resources through CloudFormation. Existing source documents, Cognito resources and DynamoDB metadata are retained. Destructive deletion of the vector resources will still require the exact Gate F confirmation at action time.
