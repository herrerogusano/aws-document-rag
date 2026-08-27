# Local development

## Prerequisites

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- Node.js 24 and npm
- AWS SAM CLI

## Complete local checks

```powershell
uv sync --locked --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
sam validate --lint
sam build

Set-Location frontend
npm ci
npm run lint
npm test -- --run
npm run build
```

These commands are credential-free and must not call AWS, ingest documents, retrieve passages, or invoke a model.

## Browser development

Copy `frontend/.env.example` to the Git-ignored `frontend/.env.local`. For the real integration, fill the public `ApiUrl`, Cognito app-client ID/domain, and local redirect URI from CloudFormation outputs. They are identifiers and endpoints, not credentials.

```powershell
Set-Location frontend
npm run dev
```

The configured app uses Cognito Authorization Code + PKCE and the protected API. Without Cognito configuration, injectable mock document/query adapters provide a credential-free local UI and deterministic component tests. Production builds receive exact public stack outputs and do not select those mocks.

Tokens remain in browser session storage and must never be copied into tickets, terminal output, logs, screenshots, or committed files. Keep `.env.local` untracked.

## Deployment

Local checks do not deploy. Follow `docs/manual-deployment.md` for the reviewed manual path or merge through the documented GitHub OIDC flow in `docs/cicd.md`.
