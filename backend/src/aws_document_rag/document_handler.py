"""Authenticated, owner-scoped document metadata API."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from functools import cache
from typing import Any

import boto3
from boto3.dynamodb.conditions import Key
from botocore.config import Config
from botocore.exceptions import ClientError

from .documents import create_document_key, validate_upload_size
from .ingestion_metadata import metadata_sidecar_key, serialize_metadata_sidecar


@cache
def _s3_client() -> Any:
    region = os.environ["AWS_REGION"]
    return boto3.client(
        "s3",
        region_name=region,
        endpoint_url=f"https://s3.{region}.amazonaws.com",
        config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
    )


@cache
def _documents_table() -> Any:
    return boto3.resource("dynamodb").Table(os.environ["DOCUMENTS_TABLE"])


def _bucket() -> str:
    return os.environ["DOCUMENTS_BUCKET"]


def _owner(event: dict[str, Any]) -> str:
    claims = event["requestContext"]["authorizer"]["jwt"]["claims"]
    return str(claims["sub"])


def _response(status: int, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(payload),
    }


def _public_document(item: dict[str, Any]) -> dict[str, Any]:
    return {
        key: item[key]
        for key in ("documentId", "filename", "status", "createdAt", "updatedAt", "sizeBytes")
        if key in item
    }


def documents(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    """Dispatch authenticated document routes without accepting an owner from the client."""
    try:
        route = event.get("routeKey")
        if route == "POST /documents/presign":
            return presign(event)
        if route == "GET /documents":
            owner = _owner(event)
            records = (
                _documents_table()
                .query(KeyConditionExpression=Key("ownerId").eq(owner))
                .get("Items", [])
            )
            return _response(200, {"documents": [_public_document(item) for item in records]})
        if route == "GET /documents/{id}":
            return get_document(event)
        if route == "POST /documents/{id}/finalize":
            return finalize_document(event)
        return _response(404, {"error": "Route not found"})
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return _response(400, {"error": "Invalid document request"})
    except ClientError:
        return _response(503, {"error": "Document service temporarily unavailable"})


def get_document(event: dict[str, Any]) -> dict[str, Any]:
    owner = _owner(event)
    document_id = str(event["pathParameters"]["id"])
    item = (
        _documents_table().get_item(Key={"ownerId": owner, "documentId": document_id}).get("Item")
    )
    if not item:
        return _response(404, {"error": "Document not found"})
    return _response(200, {"document": _public_document(item)})


def finalize_document(event: dict[str, Any]) -> dict[str, Any]:
    owner = _owner(event)
    document_id = str(event["pathParameters"]["id"])
    table = _documents_table()
    item = table.get_item(Key={"ownerId": owner, "documentId": document_id}).get("Item")
    if not item:
        return _response(404, {"error": "Document not found"})
    try:
        _s3_client().head_object(Bucket=_bucket(), Key=item["s3Key"])
    except ClientError as error:
        if error.response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 404:
            return _response(409, {"error": "Upload is not present"})
        raise
    _s3_client().put_object(
        Bucket=_bucket(),
        Key=metadata_sidecar_key(item["s3Key"]),
        Body=serialize_metadata_sidecar(owner, document_id),
        ContentType="application/json",
    )
    now = datetime.now(UTC).isoformat()
    table.update_item(
        Key={"ownerId": owner, "documentId": document_id},
        UpdateExpression="SET #status = :status, updatedAt = :updated",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={":status": "UPLOADED", ":updated": now},
    )
    item.update({"status": "UPLOADED", "updatedAt": now})
    return _response(200, {"document": _public_document(item)})


def presign(event: dict[str, Any]) -> dict[str, Any]:
    body = json.loads(event.get("body") or "{}")
    owner = _owner(event)
    filename = str(body.get("filename", ""))
    size = int(body.get("sizeBytes", 0))
    content_type = str(body.get("contentType") or "application/octet-stream")
    validate_upload_size(size)
    document_id, key = create_document_key(owner, filename)
    now = datetime.now(UTC).isoformat()
    _documents_table().put_item(
        Item={
            "ownerId": owner,
            "documentId": document_id,
            "filename": filename,
            "s3Key": key,
            "sizeBytes": size,
            "contentType": content_type,
            "status": "PENDING_UPLOAD",
            "createdAt": now,
            "updatedAt": now,
        }
    )
    url = _s3_client().generate_presigned_url(
        "put_object",
        Params={"Bucket": _bucket(), "Key": key, "ContentType": content_type},
        ExpiresIn=300,
    )
    return _response(201, {"documentId": document_id, "uploadUrl": url, "expiresIn": 300})
