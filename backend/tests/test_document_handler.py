import json
from typing import Any

from botocore.exceptions import ClientError

from aws_document_rag import document_handler


class FakeTable:
    def __init__(self, items: list[dict[str, Any]] | None = None) -> None:
        self.items = {(item["ownerId"], item["documentId"]): item for item in items or []}
        self.last_query: Any = None

    def query(self, **kwargs: Any) -> dict[str, Any]:
        self.last_query = kwargs["KeyConditionExpression"]
        owner = self.last_query._values[1]
        return {
            "Items": [item for (item_owner, _), item in self.items.items() if item_owner == owner]
        }

    def get_item(self, *, Key: dict[str, str]) -> dict[str, Any]:
        item = self.items.get((Key["ownerId"], Key["documentId"]))
        return {"Item": item} if item else {}

    def put_item(self, *, Item: dict[str, Any]) -> None:
        self.items[(Item["ownerId"], Item["documentId"])] = Item

    def update_item(self, *, Key: dict[str, str], **_kwargs: Any) -> None:
        self.items[(Key["ownerId"], Key["documentId"])]["status"] = "UPLOADED"


class FakeS3:
    def __init__(self, missing: bool = False) -> None:
        self.missing = missing
        self.presign_kwargs: dict[str, Any] = {}

    def head_object(self, **_kwargs: Any) -> None:
        if self.missing:
            raise ClientError(
                {"Error": {"Code": "404"}, "ResponseMetadata": {"HTTPStatusCode": 404}},
                "HeadObject",
            )

    def generate_presigned_url(self, _operation: str, **kwargs: Any) -> str:
        self.presign_kwargs = kwargs
        return "https://private-upload.example/presigned"


def event(route: str, owner: str = "owner-a", document_id: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "routeKey": route,
        "requestContext": {"authorizer": {"jwt": {"claims": {"sub": owner}}}},
    }
    if document_id:
        result["pathParameters"] = {"id": document_id}
    return result


def document(owner: str, document_id: str) -> dict[str, Any]:
    return {
        "ownerId": owner,
        "documentId": document_id,
        "filename": "notes.txt",
        "s3Key": f"users/{owner}/documents/{document_id}/source.txt",
        "status": "PENDING_UPLOAD",
        "createdAt": "2026-08-27T00:00:00Z",
        "updatedAt": "2026-08-27T00:00:00Z",
        "sizeBytes": 4,
    }


def test_list_and_get_are_scoped_to_jwt_owner(monkeypatch: Any) -> None:
    table = FakeTable([document("owner-a", "a"), document("owner-b", "b")])
    monkeypatch.setattr(document_handler, "_documents_table", lambda: table)

    listed = document_handler.documents(event("GET /documents"), None)
    hidden = document_handler.documents(event("GET /documents/{id}", document_id="b"), None)

    assert [item["documentId"] for item in json.loads(listed["body"])["documents"]] == ["a"]
    assert hidden["statusCode"] == 404


def test_presign_uses_server_key_and_bounded_expiration(monkeypatch: Any) -> None:
    table = FakeTable()
    s3 = FakeS3()
    monkeypatch.setattr(document_handler, "_documents_table", lambda: table)
    monkeypatch.setattr(document_handler, "_s3_client", lambda: s3)
    monkeypatch.setattr(document_handler, "_bucket", lambda: "private-bucket")
    request = event("POST /documents/presign")
    request["body"] = json.dumps(
        {"filename": "notes.txt", "sizeBytes": 4, "contentType": "text/plain"}
    )

    response = document_handler.documents(request, None)
    created = next(iter(table.items.values()))

    assert response["statusCode"] == 201
    assert created["s3Key"].startswith("users/owner-a/documents/")
    assert s3.presign_kwargs["ExpiresIn"] == 300


def test_finalize_requires_existing_private_object(monkeypatch: Any) -> None:
    table = FakeTable([document("owner-a", "a")])
    monkeypatch.setattr(document_handler, "_documents_table", lambda: table)
    monkeypatch.setattr(document_handler, "_s3_client", lambda: FakeS3(missing=True))
    monkeypatch.setattr(document_handler, "_bucket", lambda: "private-bucket")

    response = document_handler.documents(
        event("POST /documents/{id}/finalize", document_id="a"), None
    )

    assert response["statusCode"] == 409
    assert table.items[("owner-a", "a")]["status"] == "PENDING_UPLOAD"


def test_dynamodb_error_is_sanitized(monkeypatch: Any) -> None:
    class BrokenTable:
        def query(self, **_kwargs: Any) -> None:
            raise ClientError({"Error": {"Code": "InternalError"}}, "Query")

    monkeypatch.setattr(document_handler, "_documents_table", lambda: BrokenTable())
    response = document_handler.documents(event("GET /documents"), None)

    assert response["statusCode"] == 503
    assert "InternalError" not in response["body"]
