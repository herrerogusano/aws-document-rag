# Decisions

## Phase 0

- Use Python 3.13 locally and `python3.13` for future Lambda functions. AWS lists it as a
  supported Amazon Linux 2023 Lambda runtime; verified on 2026-08-27.
- Use `uv` for the backend, Ruff for formatting/linting, mypy in strict mode, and pytest.
- Use React + TypeScript + Vite for the frontend shell.
- Keep SAM resource-free until Gate A. CI performs validation only and never authenticates to AWS.

## Phase 2

- Use Cognito Hosted UI (classic version 1) with Authorization Code + PKCE. It works with the current Lite user-pool tier and keeps passwords out of the SPA.
- The browser validates its completed session by calling the JWT-protected `/me` endpoint. Tokens remain in browser session storage and are never logged.
- Local Cognito/API identifiers live only in ignored `frontend/.env.local`; committed configuration is a placeholder-only `.env.example`.
