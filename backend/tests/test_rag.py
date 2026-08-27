import pytest

from aws_document_rag.rag import (
    MAX_CHUNK_CHARS,
    normalize_retrieval_results,
    validate_question,
)


def test_question_is_required_and_bounded() -> None:
    assert validate_question("  question  ") == "question"
    with pytest.raises(ValueError):
        validate_question("")
    with pytest.raises(ValueError):
        validate_question("x" * 1_001)


def test_retrieved_chunks_are_owner_checked_and_truncated() -> None:
    results = [
        {
            "content": {"text": "a" * (MAX_CHUNK_CHARS + 10)},
            "metadata": {"owner_sub": "owner-a", "document_id": "doc-a"},
        },
        {
            "content": {"text": "private"},
            "metadata": {"owner_sub": "owner-b", "document_id": "doc-b"},
        },
    ]

    chunks = normalize_retrieval_results(results, "owner-a")

    assert len(chunks) == 1
    assert len(chunks[0]["text"]) == MAX_CHUNK_CHARS
