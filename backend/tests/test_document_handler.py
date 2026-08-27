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
        items = [item for (item_owner, _), item in self.items.items() if item_owner == owner]
        if kwargs.get("Select") == "COUNT":
            return {"Count": min(len(items), int(kwargs.get("Limit", len(items))))}
        return {"Items": items[: int(kwargs.get("Limit", len(items)))]}

    def get_item(self, *, Key: dict[str, str]) -> dict[str, Any]:
        item = self.items.get((Key["ownerId"], Key["documentId"]))
        return {"Item": item} if item else {}

    def put_item(self, *, Item: dict[str, Any]) -> None:
        self.items[(Item["ownerId"], Item["documentId"])] = Item

    def update_item(self, *, Key: dict[str, str], **_kwargs: Any) -> None:
        item = self.items[(Key["ownerId"], Key["documentId"])]
        values = _kwargs["ExpressionAttributeValues"]
        item["status"] = values[":status"]
        if ":job" in values:
            item["ingestionJobId"] = values[":job"]
        if ":error" in values:
            item["errorCode"] = values[":error"]


class FakeS3:
    def __init__(self, missing: bool = False) -> None:
        self.missing = missing
        self.presign_kwargs: dict[str, Any] = {}
        self.put_kwargs: dict[str, Any] = {}

    def head_object(self, **_kwargs: Any) -> None:
        if self.missing:
            raise ClientError(
                {"Error": {"Code": "404"}, "ResponseMetadata": {"HTTPStatusCode": 404}},
                "HeadObject",
            )

    def generate_presigned_url(self, _operation: str, **kwargs: Any) -> str:
        self.presign_kwargs = kwargs
        return "https://private-upload.example/presigned"

    def put_object(self, **kwargs: Any) -> None:
        self.put_kwargs = kwargs


class FakeBedrockAgent:
    def __init__(self, status: str = "IN_PROGRESS") -> None:
        self.status = status
        self.start_calls = 0

    def start_ingestion_job(self, **_kwargs: Any) -> dict[str, Any]:
        self.start_calls += 1
        return {"ingestionJob": {"ingestionJobId": "job-a", "status": "STARTING"}}

    def get_ingestion_job(self, **_kwargs: Any) -> dict[str, Any]:
        return {"ingestionJob": {"ingestionJobId": "job-a", "status": self.status}}


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


def test_presign_rejects_more_than_twenty_documents(monkeypatch: Any) -> None:
    table = FakeTable([document("owner-a", str(index)) for index in range(20)])
    s3 = FakeS3()
    monkeypatch.setattr(document_handler, "_documents_table", lambda: table)
    monkeypatch.setattr(document_handler, "_s3_client", lambda: s3)
    request = event("POST /documents/presign")
    request["body"] = json.dumps(
        {"filename": "notes.txt", "sizeBytes": 4, "contentType": "text/plain"}
    )

    response = document_handler.documents(request, None)

    assert response["statusCode"] == 409
    assert s3.presign_kwargs == {}


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


def test_finalize_writes_owner_metadata_sidecar(monkeypatch: Any) -> None:
    table = FakeTable([document("owner-a", "a")])
    s3 = FakeS3()
    monkeypatch.setattr(document_handler, "_documents_table", lambda: table)
    monkeypatch.setattr(document_handler, "_s3_client", lambda: s3)
    monkeypatch.setattr(document_handler, "_bucket", lambda: "private-bucket")

    response = document_handler.documents(
        event("POST /documents/{id}/finalize", document_id="a"), None
    )

    sidecar = json.loads(s3.put_kwargs["Body"])
    assert response["statusCode"] == 200
    assert s3.put_kwargs["Key"].endswith("source.txt.metadata.json")
    assert sidecar["metadataAttributes"] == {
        "owner_sub": "owner-a",
        "document_id": "a",
    }


def test_finalize_never_regresses_an_ingesting_document(monkeypatch: Any) -> None:
    item = document("owner-a", "a")
    item["status"] = "INGESTING"
    table = FakeTable([item])
    s3 = FakeS3()
    monkeypatch.setattr(document_handler, "_documents_table", lambda: table)
    monkeypatch.setattr(document_handler, "_s3_client", lambda: s3)

    response = document_handler.documents(
        event("POST /documents/{id}/finalize", document_id="a"), None
    )

    assert response["statusCode"] == 200
    assert table.items[("owner-a", "a")]["status"] == "INGESTING"
    assert s3.put_kwargs == {}


def test_dynamodb_error_is_sanitized(monkeypatch: Any) -> None:
    class BrokenTable:
        def query(self, **_kwargs: Any) -> None:
            raise ClientError({"Error": {"Code": "InternalError"}}, "Query")

    monkeypatch.setattr(document_handler, "_documents_table", lambda: BrokenTable())
    response = document_handler.documents(event("GET /documents"), None)

    assert response["statusCode"] == 503
    assert "InternalError" not in response["body"]


def test_ingestion_is_owner_scoped_and_not_started_twice(monkeypatch: Any) -> None:
    item = document("owner-a", "a")
    item["status"] = "UPLOADED"
    table = FakeTable([item])
    bedrock = FakeBedrockAgent()
    monkeypatch.setattr(document_handler, "_documents_table", lambda: table)
    monkeypatch.setattr(document_handler, "_s3_client", lambda: FakeS3())
    monkeypatch.setattr(document_handler, "_bedrock_agent", lambda: bedrock)
    monkeypatch.setattr(document_handler, "_bucket", lambda: "private-bucket")
    monkeypatch.setenv("KNOWLEDGE_BASE_ID", "knowledge-a")
    monkeypatch.setenv("KNOWLEDGE_BASE_DATA_SOURCE_ID", "source-a")

    started = document_handler.documents(
        event("POST /documents/{id}/ingest", document_id="a"), None
    )
    duplicate = document_handler.documents(
        event("POST /documents/{id}/ingest", document_id="a"), None
    )
    other_owner = document_handler.documents(
        event("POST /documents/{id}/ingest", owner="owner-b", document_id="a"), None
    )

    assert started["statusCode"] == 202
    assert duplicate["statusCode"] == 409
    assert other_owner["statusCode"] == 404
    assert bedrock.start_calls == 1


def test_status_reconciliation_maps_complete_to_ready(monkeypatch: Any) -> None:
    item = document("owner-a", "a")
    item.update({"status": "INGESTING", "ingestionJobId": "job-a"})
    table = FakeTable([item])
    monkeypatch.setattr(document_handler, "_documents_table", lambda: table)
    monkeypatch.setattr(
        document_handler, "_bedrock_agent", lambda: FakeBedrockAgent(status="COMPLETE")
    )
    monkeypatch.setenv("KNOWLEDGE_BASE_ID", "knowledge-a")
    monkeypatch.setenv("KNOWLEDGE_BASE_DATA_SOURCE_ID", "source-a")

    response = document_handler.documents(event("GET /documents/{id}", document_id="a"), None)

    assert response["statusCode"] == 200
    assert json.loads(response["body"])["document"]["status"] == "READY"


def test_ingestion_rejects_document_above_approved_limit(monkeypatch: Any) -> None:
    item = document("owner-a", "a")
    item.update({"status": "UPLOADED", "sizeBytes": 100 * 1024 + 1})
    table = FakeTable([item])
    bedrock = FakeBedrockAgent()
    monkeypatch.setattr(document_handler, "_documents_table", lambda: table)
    monkeypatch.setattr(document_handler, "_bedrock_agent", lambda: bedrock)

    response = document_handler.documents(
        event("POST /documents/{id}/ingest", document_id="a"), None
    )

    assert response["statusCode"] == 409
    assert bedrock.start_calls == 0
