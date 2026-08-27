# Deterministic manual deployment

Run from the repository root with an authenticated AWS CLI session. Public stack outputs are read at build time; no credential is placed in the bundle.

## Backend and infrastructure

```powershell
sam build
sam deploy --stack-name aws-document-rag-dev --region eu-west-1 `
  --s3-bucket aws-sam-cli-managed-default-samclisourcebucket-tptpcw2u9y7f `
  --capabilities CAPABILITY_IAM `
  --parameter-overrides AllowedFrontendOrigin=http://localhost:5173 `
  --no-confirm-changeset --no-fail-on-empty-changeset
```

Inspect the change set before any production use. CloudFormation rollback remains enabled.

## Production frontend build

The deterministic implementation of the build/publish steps is `scripts/deploy-frontend.ps1`. After the infrastructure deployment completes, run:

```powershell
.\scripts\deploy-frontend.ps1
```

If a running local Vite process locks a native dependency on Windows, stop it before `npm ci`. `-SkipInstall` is available only when the existing `node_modules` was already installed from the committed lockfile and verified in the current session.

The equivalent explicit steps are retained below for auditability.

Read `ApiUrl`, `UserPoolClientId`, `ManagedLoginUrl` and `FrontendUrl` from stack outputs. Set them only as build-process environment variables:

```powershell
$env:VITE_API_BASE_URL = '<ApiUrl>'
$env:VITE_COGNITO_CLIENT_ID = '<UserPoolClientId>'
$env:VITE_COGNITO_DOMAIN = '<ManagedLoginUrl>'
$env:VITE_COGNITO_REDIRECT_URI = '<FrontendUrl>/'
Set-Location frontend
npm ci
npm run lint
npm test -- --run
npm run build
```

## Publish immutable assets and the shell

Read `FrontendBucketName` and `FrontendDistributionId` from stack outputs. Upload hashed assets with immutable caching, then upload the shell without caching. This sequence does not delete any object:

```powershell
aws s3 cp dist/assets "s3://<FrontendBucketName>/assets" --recursive `
  --cache-control "public,max-age=31536000,immutable"
aws s3 cp dist/index.html "s3://<FrontendBucketName>/index.html" `
  --cache-control "no-cache,max-age=0" --content-type "text/html"
aws cloudfront create-invalidation --distribution-id <FrontendDistributionId> --paths "/*"
```

Old hashed assets can be reviewed and removed in a separately approved exact cleanup; routine deployment does not use `sync --delete`.

## Smoke checks

1. `FrontendUrl` returns HTTPS 200 and the S3 object URL returns access denied.
2. Cognito app-client callbacks/logout include the exact frontend URL.
3. Sign in, confirm only the owner's documents appear, and use the already indexed tiny document.
4. Ask at most one bounded question, verify at least one citation, and do not log the answer/source text.
5. Confirm API/Lambda logs contain correlation/status/count fields only and no tokens, question, answer, document text, presigned URL or S3 key.

Rollback the frontend artifact by uploading the previous `index.html` and matching hashed assets, then invalidate `/*`. Roll back infrastructure with the previous reviewed SAM template/change set; do not delete data resources.
