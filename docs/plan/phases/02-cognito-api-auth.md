# Phase 2 — Cognito authentication and protected API skeleton

## Goal

Replace mocked identity with real AWS authentication and establish a protected backend boundary.

## Target flow

```text
React
→ Cognito User Pool managed login / OAuth2 Authorization Code + PKCE
→ JWT
→ API Gateway HTTP API JWT authorizer
→ Lambda
```

## Design

- Cognito User Pool.
- Public app client for browser use; no client secret in frontend.
- Managed login/hosted authentication flow unless a strong reason exists to build custom password UI.
- Authorization Code + PKCE for SPA.
- API Gateway HTTP API with JWT authorizer backed by Cognito issuer/audience.
- Minimal authenticated route such as `GET /me` or `GET /health/auth` returning only non-sensitive claims needed by the app.
- Use Cognito `sub` as stable owner ID.

## Security

- API Gateway must reject missing/invalid JWT before Lambda on protected routes.
- Do not trust email as ownership key.
- Do not log raw JWTs or refresh/access tokens.
- CORS restricted to known local frontend origin during development; no `*` with credentials.
- No Cognito user password stored in repo/vault logs.

## First AWS gate

This phase may be the first AWS deployment. Before deploying, execute Gate A from `GATES.md` and stop for approval.

After approval, the approved baseline may include Cognito, HTTP API, minimal Lambda, IAM and logs. Routine updates within that envelope can continue autonomously.

## Frontend

Replace mock auth with real auth while keeping the abstraction.

Handle:
- sign in;
- callback;
- sign out;
- token refresh through supported library/flow;
- authenticated API request.

Do not implement custom token parsing as an authorization mechanism.

## Tests

CI remains offline:
- auth-state unit tests;
- API JWT config/template assertions;
- handler tests with synthetic validated claims context;
- CORS tests;
- secret leakage tests.

## Acceptance criteria

- Local frontend can sign in through Cognito after approved deployment.
- Protected endpoint works with valid auth and rejects unauthenticated calls.
- No AWS credentials in browser.
- CI still uses no AWS.
