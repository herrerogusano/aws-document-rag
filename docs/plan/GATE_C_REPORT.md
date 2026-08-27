# Gate C report — first generative RAG call

> Historical baseline: Nova Micro was the initially approved model. The active model was upgraded to Nova Lite under `GATE_C_NOVA_LITE_ADDENDUM.md` on 2026-08-28 without relaxing any token, retry, isolation, or monthly-call bound.

Prepared 2026-08-27 from current AWS documentation and the AWS Price List API for `eu-west-1`.

## Bounded configuration

- Model: Amazon Nova Micro, EU inference profile `eu.amazon.nova-micro-v1:0` through the Bedrock Converse API.
- Source region: `eu-west-1`; the EU profile keeps processing within its documented EU destination Regions.
- Retrieval: maximum 5 owner-filtered chunks; optional document filter can only narrow the owner filter.
- Prompt/context: question at most 1,000 characters; each retrieved chunk truncated to 2,000 characters; total application context bounded below 12,000 characters.
- Generation: maximum 256 output tokens, temperature `0.1`, one model invocation per query and no automatic retry.
- Prompt states that retrieved document text is untrusted data and cannot override application instructions.
- Zero retrieval results return an insufficient-context response without invoking the model.
- First live validation: one question against the already approved tiny document. Output text/content will not be logged; only non-empty answer, citation and owner-isolation booleans are inspected.
- Monthly development ceiling: at most 100 generative queries. No provisioned throughput, prompt caching, reranking or agents.

## Current pricing

The AWS Price List API returned these `eu-west-1` Nova Micro on-demand rates on 2026-08-27:

- Input: **$0.00004 per 1,000 tokens**.
- Output: **$0.00016 per 1,000 tokens**.

A deliberately conservative 4,000-token input plus the full 256-token output costs about **$0.000201** for generation. Including retrieval/query embeddings and S3 Vectors at this project scale, the expected bounded total remains below **$0.001 per query** and below **$0.10 for 100 development queries**. No Free Tier assumption is used.

Official references:

- [Nova Micro model and EU inference profile](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-micro.html)
- [Model regional compatibility](https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html)
- [Nova Converse support](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-nova.html)
- [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)

## Failure and rollback

- Retrieval or generation errors are sanitized; no retry doubles the model cost.
- Citations are produced only from retrieved chunks whose owner metadata matches the authenticated Cognito `sub`.
- Rollback is disabling/removing the query route or its Lambda model permission. The Knowledge Base, vectors and source documents remain intact.

## Authorization

The user explicitly authorized autonomous progression through successive gates on 2026-08-27. Gate C is therefore approved only for the configuration and limits above. Gate D/E/F remain separate.
