import json

import pytest

from aws_document_rag.ingestion_metadata import (
    MAX_SIDECAR_BYTES,
    metadata_sidecar,
    metadata_sidecar_key,
    serialize_metadata_sidecar,
)


def test_sidecar_is_adjacent_to_source_document() -> None:
    assert (
        metadata_sidecar_key("users/owner/documents/doc/source.txt")
        == "users/owner/documents/doc/source.txt.metadata.json"
    )


def test_owner_and_document_are_always_filterable_metadata() -> None:
    payload = metadata_sidecar("owner-a", "document-a")
    assert payload == {
        "metadataAttributes": {
            "owner_sub": "owner-a",
            "document_id": "document-a",
        }
    }
    assert "includeForEmbedding" not in json.dumps(payload)


def test_sidecar_is_valid_utf8_json_within_service_limit() -> None:
    serialized = serialize_metadata_sidecar("owner-a", "document-a")
    assert json.loads(serialized) == metadata_sidecar("owner-a", "document-a")
    assert len(serialized) < MAX_SIDECAR_BYTES


@pytest.mark.parametrize(("owner", "document_id"), [("", "document-a"), ("owner-a", "")])
def test_identifiers_are_required(owner: str, document_id: str) -> None:
    with pytest.raises(ValueError):
        serialize_metadata_sidecar(owner, document_id)
