# Local development

## Prerequisites

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- Node.js 24
- AWS SAM CLI (validation only in Phase 0)

## Checks

```powershell
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
sam validate --lint

Set-Location frontend
npm ci
npm run lint
npm run build
```

These checks are offline: they neither authenticate to AWS nor invoke Bedrock.

## Local Cognito configuration

Copy `.env.example` to `.env.local` inside `frontend/` and set only public configuration values.
The local file is ignored by Git. Run `npm run dev` from `frontend/`, then use the Cognito
Hosted UI flow. The app uses Authorization Code + PKCE and validates the resulting JWT against
the protected `/me` endpoint without printing tokens.
