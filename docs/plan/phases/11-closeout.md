# Phase 11 — Demo, portfolio documentation, interview preparation and closure

## Goal

Close the project without adding architecture for its own sake.

## Final README

Explain:
- problem and user flow;
- architecture diagrams (runtime and CI/CD separately);
- RAG lifecycle;
- why Cognito/API Gateway/Lambda/S3/DynamoDB/Knowledge Bases/S3 Vectors/Bedrock;
- security and per-user isolation;
- cost controls;
- CI/CD;
- local development/deployment;
- limitations and future improvements.

Assume repository may be public. Sanitize account IDs, user IDs, URLs containing identifying info and all secrets.

## Demo

Prepare a repeatable demo:
1. open hosted frontend;
2. sign in with demo user;
3. show document list;
4. upload small sanitized document;
5. show ingestion state;
6. ask a question;
7. show grounded answer and citation;
8. show GitHub CI/CD and high-level CloudWatch evidence.

Bound model/ingestion calls and do not create repeated costs for documentation.

## Interview material

Create local/vault docs for questions such as:
- What is RAG?
- Why embeddings?
- What is a vector database/vector store?
- Why not send the entire PDF to the LLM?
- What does Bedrock Knowledge Bases manage?
- S3 vs S3 Vectors?
- Why DynamoDB if vectors are elsewhere?
- Why presigned URLs?
- Cognito User Pool and JWT flow?
- API Gateway JWT authorizer?
- IAM role separation?
- How is tenant/user isolation guaranteed?
- What is prompt injection in RAG?
- Why Lambda vs EC2/Fargate?
- SAM vs CloudFormation vs Terraform?
- CI vs CD and why CI started earlier?
- GitHub OIDC and bootstrap?
- Where can this architecture cost money?

Include 20-second, 2-minute and deep technical explanations.

## Final audits

Run:
- all backend/frontend checks;
- SAM validate/build;
- security/isolation tests;
- secret scan;
- IAM review;
- cost inventory review;
- deployed resource inventory;
- CI/CD latest status;
- git status.

## Cleanup

Remove dead code, mocks unused in production, stale TODOs and duplicate docs. Do not delete AWS data/resources automatically.

## Closure criteria

Only mark complete if:
- authenticated full-stack flow works;
- per-user RAG isolation is tested;
- manual and automatic deployment paths are understood/proven;
- CI/CD is green;
- costs/security are documented;
- project can be explained in interview.

Propose final commit/PR and merge autonomously if it does not cross a pending gate.
