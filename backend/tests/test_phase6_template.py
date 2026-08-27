from pathlib import Path

TEMPLATE = (Path(__file__).parents[2] / "template.yaml").read_text(encoding="utf-8")


def test_query_route_is_authenticated_by_default() -> None:
    assert "Path: /query" in TEMPLATE
    assert "DefaultAuthorizer: CognitoJwt" in TEMPLATE
    assert "Handler: aws_document_rag.query_handler.query" in TEMPLATE


def test_generation_permission_is_bounded_to_approved_model() -> None:
    assert "GENERATION_MODEL_ID: eu.amazon.nova-lite-v1:0" in TEMPLATE
    assert "amazon.nova-micro-v1:0" not in TEMPLATE
    assert "bedrock:InvokeModel" in TEMPLATE
    assert "bedrock:*" not in TEMPLATE
    assert 'Resource: "*"' not in TEMPLATE
    assert "InvokeModelWithResponseStream" not in TEMPLATE


def test_query_has_no_automatic_retry_or_retrieve_and_generate() -> None:
    assert "RetrieveAndGenerate" not in TEMPLATE
    assert "bedrock:Retrieve" in TEMPLATE
