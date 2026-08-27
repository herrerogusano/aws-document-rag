param(
    [string]$StackName = "aws-document-rag-dev",
    [string]$Region = "eu-west-1",
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"

$stack = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query "Stacks[0].Outputs" `
    --output json | ConvertFrom-Json

if ($LASTEXITCODE -ne 0) { throw "Could not read stack outputs." }

function Get-StackOutput([string]$Key) {
    $value = ($stack | Where-Object OutputKey -eq $Key).OutputValue
    if (-not $value) { throw "Missing required stack output: $Key" }
    return $value
}

$apiUrl = Get-StackOutput "ApiUrl"
$clientId = Get-StackOutput "UserPoolClientId"
$cognitoDomain = Get-StackOutput "ManagedLoginUrl"
$frontendUrl = Get-StackOutput "FrontendUrl"
$frontendBucket = Get-StackOutput "FrontendBucketName"
$distributionId = Get-StackOutput "FrontendDistributionId"

Push-Location "$PSScriptRoot\..\frontend"
try {
    $env:VITE_API_BASE_URL = $apiUrl
    $env:VITE_COGNITO_CLIENT_ID = $clientId
    $env:VITE_COGNITO_DOMAIN = $cognitoDomain
    $env:VITE_COGNITO_REDIRECT_URI = "$frontendUrl/"
    if (-not $SkipInstall) {
        npm ci
        if ($LASTEXITCODE -ne 0) { throw "npm ci failed. Stop any local dev server or use -SkipInstall with an already verified node_modules tree." }
    }
    npm run lint
    if ($LASTEXITCODE -ne 0) { throw "Frontend lint failed." }
    npm test -- --run
    if ($LASTEXITCODE -ne 0) { throw "Frontend tests failed." }
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "Frontend build failed." }

    aws s3 cp dist/assets "s3://$frontendBucket/assets" `
        --recursive `
        --cache-control "public,max-age=31536000,immutable" `
        --region $Region
    if ($LASTEXITCODE -ne 0) { throw "Asset upload failed." }
    aws s3 cp dist/index.html "s3://$frontendBucket/index.html" `
        --cache-control "no-cache,max-age=0" `
        --content-type "text/html" `
        --region $Region
    if ($LASTEXITCODE -ne 0) { throw "Shell upload failed." }
    aws cloudfront create-invalidation `
        --distribution-id $distributionId `
        --paths "/*" | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "CloudFront invalidation failed." }
}
finally {
    Pop-Location
}

Write-Output "Frontend deployment submitted: $frontendUrl"
