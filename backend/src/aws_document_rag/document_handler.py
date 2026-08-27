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

from .aws_config import STANDARD_AWS_CONFIG
from .documents import MAX_DOCUMENTS_PER_USER, create_document_key, validate_upload_size
from .ingestion_metadata import (
    MAX_INGESTION_BYTES,
    metadata_sidecar_key,
    serialize_metadata_sidecar,
)
from .observability import log_event


class DocumentLimitError(ValueError):
    """Raised when a development account reaches its bounded document count."""


@cache
def _s3_client() -> Any:
    region = os.environ["AWS_REGION"]
    return boto3.client(
        "s3",
        region_name=region,
        endpoint_url=f"https://s3.{region}.amazonaws.com",
        config=STANDARD_AWS_CONFIG.merge(
            Config(signature_version="s3v4", s3={"addressing_style": "virtual"})
        ),
    )


@cache
def _documents_table() -> Any:
    return boto3.resource("dynamodb", config=STANDARD_AWS_CONFIG).Table(
        os.environ["DOCUMENTS_TABLE"]
    )


@cache
def _bedrock_agent() -> Any:
    return boto3.client(
        "bedrock-agent", region_name=os.environ["AWS_REGION"], config=STANDARD_AWS_CONFIG
    )


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
        for key in (
            "documentId",
            "filename",
            "status",
            "createdAt",
            "updatedAt",
            "sizeBytes",
            "errorCode",
        )
        if key in item
    }


def documents(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Dispatch authenticated document routes without accepting an owner from the client."""
    try:
        route = event.get("routeKey")
        if route == "POST /documents/presign":
            return presign(event)
        if route == "GET /documents":
            owner = _owner(event)
            records = (
                _documents_table()
                .query(
                    KeyConditionExpression=Key("ownerId").eq(owner), Limit=MAX_DOCUMENTS_PER_USER
                )
                .get("Items", [])
            )
            response = _response(200, {"documents": [_public_document(item) for item in records]})
            log_event("documents_listed", event, context, statusCode=200, count=len(records))
            return response
        if route == "GET /documents/{id}":
            return get_document(event)
        if route == "POST /documents/{id}/finalize":
            return finalize_document(event)
        if route == "POST /documents/{id}/ingest":
            return ingest_document(event)
        return _response(404, {"error": "Route not found"})
    except DocumentLimitError:
        log_event("document_limit_rejected", event, context, statusCode=409)
        return _response(409, {"error": "Document limit reached"})
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        log_event("document_request_rejected", event, context, statusCode=400)
        return _response(400, {"error": "Invalid document request"})
    except ClientError:
        log_event("document_service_error", event, context, statusCode=503)
        return _response(503, {"error": "Document service temporarily unavailable"})


def get_document(event: dict[str, Any]) -> dict[str, Any]:
    owner = _owner(event)
    document_id = str(event["pathParameters"]["id"])
    item = (
        _documents_table().get_item(Key={"ownerId": owner, "documentId": document_id}).get("Item")
    )
    if not item:
        return _response(404, {"error": "Document not found"})
    item = _reconcile_ingestion(item)
    return _response(200, {"document": _public_document(item)})


def _reconcile_ingestion(item: dict[str, Any]) -> dict[str, Any]:
    if item.get("status") != "INGESTING" or not item.get("ingestionJobId"):
        return item
    job = _bedrock_agent().get_ingestion_job(
        knowledgeBaseId=os.environ["KNOWLEDGE_BASE_ID"],
        dataSourceId=os.environ["KNOWLEDGE_BASE_DATA_SOURCE_ID"],
        ingestionJobId=item["ingestionJobId"],
    )["ingestionJob"]
    mapped_status = {
        "COMPLETE": "READY",
        "FAILED": "FAILED",
        "STOPPED": "FAILED",
    }.get(job["status"], "INGESTING")
    if mapped_status == "INGESTING":
        return item
    now = datetime.now(UTC).isoformat()
    update = "SET #status = :status, updatedAt = :updated"
    values = {":status": mapped_status, ":updated": now}
    if mapped_status == "FAILED":
        update += ", errorCode = :error"
        values[":error"] = "INGESTION_FAILED"
        item["errorCode"] = "INGESTION_FAILED"
    _documents_table().update_item(
        Key={"ownerId": item["ownerId"], "documentId": item["documentId"]},
        UpdateExpression=update,
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues=values,
    )
    item.update({"status": mapped_status, "updatedAt": now})
    return item


def finalize_document(event: dict[str, Any]) -> dict[str, Any]:
    owner = _owner(event)
    document_id = str(event["pathParameters"]["id"])
    table = _documents_table()
    item = table.get_item(Key={"ownerId": owner, "documentId": document_id}).get("Item")
    if not item:
        return _response(404, {"error": "Document not found"})
    if item.get("status") in {"UPLOADED", "INGESTING", "READY"}:
        return _response(200, {"document": _public_document(item)})
    if item.get("status") != "PENDING_UPLOAD":
        return _response(409, {"error": "Document cannot be finalized"})
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


def ingest_document(event: dict[str, Any]) -> dict[str, Any]:
    owner = _owner(event)
    document_id = str(event["pathParameters"]["id"])
    table = _documents_table()
    item = table.get_item(Key={"ownerId": owner, "documentId": document_id}).get("Item")
    if not item:
        return _response(404, {"error": "Document not found"})
    if item["status"] == "READY":
        return _response(200, {"document": _public_document(item)})
    if item["status"] == "INGESTING":
        return _response(409, {"error": "Document ingestion is already in progress"})
    if item["status"] != "UPLOADED":
        return _response(409, {"error": "Document is not ready for ingestion"})
    if int(item.get("sizeBytes", 0)) > MAX_INGESTION_BYTES:
        return _response(409, {"error": "Document exceeds the approved ingestion limit"})
    try:
        _s3_client().head_object(Bucket=_bucket(), Key=item["s3Key"])
        _s3_client().head_object(Bucket=_bucket(), Key=metadata_sidecar_key(item["s3Key"]))
    except ClientError as error:
        if error.response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 404:
            return _response(409, {"error": "Document upload is incomplete"})
        raise
    try:
        job = _bedrock_agent().start_ingestion_job(
            knowledgeBaseId=os.environ["KNOWLEDGE_BASE_ID"],
            dataSourceId=os.environ["KNOWLEDGE_BASE_DATA_SOURCE_ID"],
            clientToken=document_id,
            description="Authenticated document ingestion",
        )["ingestionJob"]
    except ClientError as error:
        if error.response.get("Error", {}).get("Code") == "ConflictException":
            return _response(409, {"error": "Another ingestion is already in progress"})
        raise
    now = datetime.now(UTC).isoformat()
    table.update_item(
        Key={"ownerId": owner, "documentId": document_id},
        UpdateExpression="SET #status = :status, ingestionJobId = :job, updatedAt = :updated",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={
            ":status": "INGESTING",
            ":job": job["ingestionJobId"],
            ":updated": now,
        },
    )
    item.update({"status": "INGESTING", "ingestionJobId": job["ingestionJobId"], "updatedAt": now})
    return _response(202, {"document": _public_document(item)})


def presign(event: dict[str, Any]) -> dict[str, Any]:
    body = json.loads(event.get("body") or "{}")
    owner = _owner(event)
    filename = str(body.get("filename", ""))
    size = int(body.get("sizeBytes", 0))
    content_type = str(body.get("contentType") or "application/octet-stream")
    validate_upload_size(size)
    count = (
        _documents_table()
        .query(
            KeyConditionExpression=Key("ownerId").eq(owner),
            Select="COUNT",
            Limit=MAX_DOCUMENTS_PER_USER,
        )
        .get("Count", 0)
    )
    if int(count) >= MAX_DOCUMENTS_PER_USER:
        raise DocumentLimitError
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
