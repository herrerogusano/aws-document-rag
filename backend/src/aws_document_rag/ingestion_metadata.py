"""Build filter-only Bedrock metadata sidecars for private documents."""

from __future__ import annotations

import json
from typing import Any

MAX_SIDECAR_BYTES = 10 * 1024
MAX_INGESTION_BYTES = 100 * 1024


def metadata_sidecar_key(source_key: str) -> str:
    if not source_key or source_key.endswith(".metadata.json"):
        raise ValueError("A source document key is required")
    return f"{source_key}.metadata.json"


def metadata_sidecar(owner_sub: str, document_id: str) -> dict[str, Any]:
    """Return metadata that is filterable but excluded from embedding input."""
    if not owner_sub or not document_id:
        raise ValueError("Owner and document identifiers are required")
    return {
        "metadataAttributes": {
            "owner_sub": owner_sub,
            "document_id": document_id,
        }
    }


def serialize_metadata_sidecar(owner_sub: str, document_id: str) -> bytes:
    payload = json.dumps(
        metadata_sidecar(owner_sub, document_id),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    if len(payload) > MAX_SIDECAR_BYTES:
        raise ValueError("Metadata sidecar exceeds the Bedrock limit")
    return payload
