# Decisions

## Phase 0

- Use Python 3.13 locally and `python3.13` for future Lambda functions. AWS lists it as a
  supported Amazon Linux 2023 Lambda runtime; verified on 2026-08-27.
- Use `uv` for the backend, Ruff for formatting/linting, mypy in strict mode, and pytest.
- Use React + TypeScript + Vite for the frontend shell.
- Keep SAM resource-free until Gate A. CI performs validation only and never authenticates to AWS.
