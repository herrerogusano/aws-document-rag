"""Authenticated retrieval and single-invocation grounded generation API."""

from __future__ import annotations

import json
import os
from functools import cache
from typing import Any

import boto3
from botocore.exceptions import ClientError

from .aws_config import MODEL_AWS_CONFIG, STANDARD_AWS_CONFIG
from .observability import log_event
from .rag import (
    MAX_OUTPUT_TOKENS,
    SYSTEM_PROMPT,
    citations_for_chunks,
    grounded_user_message,
    normalize_retrieval_results,
    validate_question,
)
from .retrieval import retrieval_configuration


@cache
def _runtime() -> Any:
    return boto3.client(
        "bedrock-agent-runtime",
        region_name=os.environ["AWS_REGION"],
        config=STANDARD_AWS_CONFIG,
    )


@cache
def _model_runtime() -> Any:
    return boto3.client(
        "bedrock-runtime", region_name=os.environ["AWS_REGION"], config=MODEL_AWS_CONFIG
    )


@cache
def _table() -> Any:
    return boto3.resource("dynamodb", config=STANDARD_AWS_CONFIG).Table(
        os.environ["DOCUMENTS_TABLE"]
    )


@cache
def _usage_table() -> Any:
    return boto3.resource("dynamodb", config=STANDARD_AWS_CONFIG).Table(os.environ["USAGE_TABLE"])


def _consume_generation_budget() -> None:
    from datetime import UTC, datetime

    _usage_table().update_item(
        Key={"scope": "GENERATION", "period": datetime.now(UTC).strftime("%Y-%m")},
        UpdateExpression="ADD requestCount :one",
        ConditionExpression="attribute_not_exists(requestCount) OR requestCount < :limit",
        ExpressionAttributeValues={":one": 1, ":limit": 100},
    )


def _owner(event: dict[str, Any]) -> str:
    return str(event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"])


def _response(status: int, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(payload),
    }


def _insufficient() -> dict[str, Any]:
    return _response(
        200,
        {
            "answer": "The available documents do not contain enough information to answer.",
            "citations": [],
            "insufficientContext": True,
        },
    )


def query(event: dict[str, Any], context: Any) -> dict[str, Any]:
    try:
        owner = _owner(event)
        body = json.loads(event.get("body") or "{}")
        question = validate_question(body.get("question"))
        document_id = str(body.get("documentId") or "") or None
        if document_id:
            selected = (
                _table().get_item(Key={"ownerId": owner, "documentId": document_id}).get("Item")
            )
            if not selected:
                return _response(404, {"error": "Document not found"})
            if selected.get("status") != "READY":
                return _response(409, {"error": "Document is not ready"})
        retrieved = _runtime().retrieve(
            knowledgeBaseId=os.environ["KNOWLEDGE_BASE_ID"],
            retrievalQuery={"text": question},
            retrievalConfiguration=retrieval_configuration(owner, document_id=document_id),
        )
        chunks = normalize_retrieval_results(retrieved.get("retrievalResults", []), owner)
        if not chunks:
            log_event("query_insufficient", event, context, statusCode=200, retrievedChunks=0)
            return _insufficient()
        _consume_generation_budget()
        generated = _model_runtime().converse(
            modelId=os.environ["GENERATION_MODEL_ID"],
            system=[{"text": SYSTEM_PROMPT}],
            messages=[
                {
                    "role": "user",
                    "content": [{"text": grounded_user_message(question, chunks)}],
                }
            ],
            inferenceConfig={
                "maxTokens": MAX_OUTPUT_TOKENS,
                "temperature": 0.1,
                "topP": 0.9,
            },
        )
        answer = str(generated["output"]["message"]["content"][0]["text"]).strip()
        document_ids = {chunk["documentId"] for chunk in chunks}
        filenames: dict[str, str] = {}
        for chunk_document_id in document_ids:
            item = (
                _table()
                .get_item(Key={"ownerId": owner, "documentId": chunk_document_id})
                .get("Item")
            )
            if item:
                filenames[chunk_document_id] = str(item["filename"])
        response = _response(
            200,
            {
                "answer": answer,
                "citations": citations_for_chunks(chunks, filenames),
                "insufficientContext": False,
            },
        )
        log_event(
            "query_completed",
            event,
            context,
            statusCode=200,
            retrievedChunks=len(chunks),
            citationCount=len(filenames),
        )
        return response
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        log_event("query_rejected", event, context, statusCode=400)
        return _response(400, {"error": "Invalid query request"})
    except ClientError as error:
        if error.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            log_event("query_budget_exhausted", event, context, statusCode=429)
            return _response(429, {"error": "Monthly development query limit reached"})
        log_event("query_service_error", event, context, statusCode=503)
        return _response(503, {"error": "Grounded query service temporarily unavailable"})
