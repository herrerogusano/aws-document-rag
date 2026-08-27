# Gate C addendum — Nova Lite and bounded semantic evaluation

Prepared and authorized 2026-08-28 after the user explicitly requested the Nova Lite upgrade and ambiguous-question testing.

## Exact change

- Replace the EU Nova Micro inference profile with Nova Lite: `eu.amazon.nova-lite-v1:0`.
- Replace only the query Lambda's approved inference-profile and four EU destination-model IAM ARNs.
- Preserve five retrieved chunks, 2,000 characters/chunk, 1,000-character questions, 256 output tokens, temperature 0.1, one model attempt, owner filtering, result validation, and the 100-generation monthly counter.
- Run exactly five synthetic live evaluation calls. They contain no user document, owner ID, token, secret, or retrieval operation.

AWS documents `eu.amazon.nova-lite-v1:0` as the EU geographic inference ID from `eu-west-1`, routing only among documented EU destinations. The AWS Price List API returned $0.000069/1K input tokens and $0.000276/1K output tokens for on-demand Nova Lite in EU (Ireland) on 2026-08-28.

At a conservative 4,000 input tokens plus the 256-token output ceiling, one call is about $0.00035 and the 100-call envelope is below $0.035 for generation. The five-case evaluation ceiling is below $0.002. Retrieval and other service dimensions remain separate; this estimate is not a billing guarantee.

Official references:

- [Nova Lite model card and EU inference profile](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-lite.html)
- [Cross-Region inference behavior](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html)
- [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)

## Evaluation contract

The committed suite covers five behaviors: before/after comparison, short elliptical wording with one referent, refusal when cost is absent, explicit handling of conflicting sources, and ignoring an instruction embedded inside document text. It reports pass/fail against synthetic expected facts and never runs in ordinary CI/CD.

## Rollback

Restore the prior model ID and exact Micro ARNs, deploy through the same reviewed pipeline, and retain the evaluation evidence. No document, vector, metadata record, or identity needs to change.
