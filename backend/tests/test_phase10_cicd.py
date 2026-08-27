from pathlib import Path

ROOT = Path(__file__).parents[2]
WORKFLOW = (ROOT / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")
BOOTSTRAP = (ROOT / "infrastructure" / "deployment-access.yaml").read_text(encoding="utf-8")


def test_oidc_trust_is_immutable_repository_main_only() -> None:
    assert "sts:AssumeRoleWithWebIdentity" in BOOTSTRAP
    assert (
        "repo:${GitHubOwner}@${GitHubOwnerId}/${GitHubRepository}@${GitHubRepositoryId}:ref:refs/heads/main"
        in BOOTSTRAP
    )
    assert "token.actions.githubusercontent.com:aud: sts.amazonaws.com" in BOOTSTRAP
    assert "repo:*" not in BOOTSTRAP


def test_deployment_has_no_static_credentials_or_destructive_sync() -> None:
    assert "id-token: write" in WORKFLOW
    assert "configure-aws-credentials@v6.2.3" in WORKFLOW
    assert "aws-access-key-id" not in WORKFLOW
    assert "aws-secret-access-key" not in WORKFLOW
    assert "sync --delete" not in WORKFLOW
    assert "s3:DeleteObject" not in BOOTSTRAP


def test_deployment_is_serialized_and_never_runs_live_rag() -> None:
    assert "cancel-in-progress: false" in WORKFLOW
    assert "needs: quality" in WORKFLOW
    assert "--no-fail-on-empty-changeset" in WORKFLOW
    assert "start-ingestion-job" not in WORKFLOW
    assert "bedrock-runtime" not in WORKFLOW
    assert "create-invalidation" in WORKFLOW


def test_cloudformation_execution_role_can_expand_only_the_sam_transform() -> None:
    assert "Sid: ExpandSamTransform" in BOOTSTRAP
    assert "Action: cloudformation:CreateChangeSet" in BOOTSTRAP
    assert (
        "arn:${AWS::Partition}:cloudformation:${AWS::Region}:aws:transform/Serverless-2016-10-31"
        in BOOTSTRAP
    )
