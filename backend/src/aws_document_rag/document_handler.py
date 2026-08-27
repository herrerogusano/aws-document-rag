"""Authenticated, owner-scoped document metadata API."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from typing import Any

import boto3

from .documents import create_document_key, validate_upload_size

s3 = boto3.client("s3")
table = boto3.resource("dynamodb").Table(os.environ["DOCUMENTS_TABLE"])
bucket = os.environ["DOCUMENTS_BUCKET"]


def _owner(event: dict[str, Any]) -> str:
    claims = event["requestContext"]["authorizer"]["jwt"]["claims"]
    return str(claims["sub"])


def presign(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    body = json.loads(event.get("body") or "{}")
    owner = _owner(event)
    filename = str(body.get("filename", ""))
    size = int(body.get("sizeBytes", 0))
    validate_upload_size(size)
    document_id, key = create_document_key(owner, filename)
    now = datetime.now(UTC).isoformat()
    table.put_item(
        Item={
            "ownerId": owner,
            "documentId": document_id,
            "filename": filename,
            "s3Key": key,
            "status": "PENDING_UPLOAD",
            "createdAt": now,
            "updatedAt": now,
        }
    )
    url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": bucket,
            "Key": key,
            "ContentType": str(body.get("contentType", "application/octet-stream")),
        },
        ExpiresIn=300,
    )
    return {
        "statusCode": 201,
        "headers": {"content-type": "application/json"},
        "body": json.dumps({"documentId": document_id, "uploadUrl": url, "expiresIn": 300}),
    }
