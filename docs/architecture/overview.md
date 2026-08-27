# Architecture overview

Phase 0 establishes provider-neutral contracts and a deliberately empty SAM template.
No AWS resource is defined, created, or contacted.

The planned runtime flow is React -> Cognito -> API Gateway -> Lambda, with private S3,
DynamoDB, Bedrock Knowledge Bases/S3 Vectors, and Bedrock Runtime introduced only in their
respective approved phases. Ownership will always be derived from Cognito `sub` and applied
as a mandatory retrieval filter.
