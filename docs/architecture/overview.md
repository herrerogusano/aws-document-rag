# Architecture overview

Phase 0 established provider-neutral contracts. Phase 2 now contains an undeployed SAM
definition for Cognito, a JWT-protected HTTP API, and a minimal `/me` Lambda endpoint.
No AWS resource has been created or contacted beyond credential identity verification.

The planned runtime flow is React -> Cognito -> API Gateway -> Lambda, with private S3,
DynamoDB, Bedrock Knowledge Bases/S3 Vectors, and Bedrock Runtime introduced only in their
respective approved phases. Ownership will always be derived from Cognito `sub` and applied
as a mandatory retrieval filter.
