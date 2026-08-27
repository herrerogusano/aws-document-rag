import logging
from pathlib import Path

import pytest

from aws_document_rag.observability import log_event

TEMPLATE = (Path(__file__).parents[2] / "template.yaml").read_text(encoding="utf-8")


def test_structured_log_allowlist_excludes_request_content(
    caplog: pytest.LogCaptureFixture,
) -> None:
    event = {
        "requestContext": {"requestId": "request-a"},
        "body": '{"question":"PRIVATE QUESTION","token":"SECRET TOKEN"}',
    }
    with caplog.at_level(logging.INFO):
        log_event("query_completed", event, None, statusCode=200, retrievedChunks=2)
    output = caplog.text
    assert "request-a" in output
    assert "retrievedChunks" in output
    assert "PRIVATE QUESTION" not in output
    assert "SECRET TOKEN" not in output


def test_template_bounds_logs_traffic_and_generation_cost() -> None:
    assert "RetentionInDays: 14" in TEMPLATE
    assert "ThrottlingBurstLimit: 10" in TEMPLATE
    assert "ThrottlingRateLimit: 5" in TEMPLATE
    assert "ReservedConcurrentExecutions" not in TEMPLATE
    assert "USAGE_TABLE: !Ref UsageTable" in TEMPLATE
    assert "ConditionExpression" not in TEMPLATE


def test_every_http_route_inherits_the_jwt_authorizer() -> None:
    assert "DefaultAuthorizer: CognitoJwt" in TEMPLATE
    assert "Authorizer: NONE" not in TEMPLATE
    assert "AllowOrigins: [!Ref AllowedFrontendOrigin]" in TEMPLATE
    assert "BlockPublicAcls: true" in TEMPLATE
    assert "RestrictPublicBuckets: true" in TEMPLATE
