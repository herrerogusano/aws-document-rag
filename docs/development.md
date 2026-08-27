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
