import json

from aws_document_rag.auth_handler import me


def test_me_returns_only_validated_sub_claim() -> None:
    response = me({"requestContext": {"authorizer": {"jwt": {"claims": {"sub": "owner-a"}}}}}, None)

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"ownerId": "owner-a"}


def test_me_rejects_missing_claims() -> None:
    response = me({}, None)

    assert response["statusCode"] == 401
    assert "ownerId" not in response["body"]
