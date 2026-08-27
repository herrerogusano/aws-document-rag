from datetime import UTC, datetime

from aws_document_rag import Citation, DocumentRecord, DocumentStatus, QueryAnswer, QueryRequest


def test_document_record_uses_safe_application_metadata() -> None:
    record = DocumentRecord(
        document_id="doc-123",
        filename="notes.pdf",
        status=DocumentStatus.PENDING_UPLOAD,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    assert record.status is DocumentStatus.PENDING_UPLOAD
    assert not hasattr(record, "s3_key")


def test_query_answer_citations_are_explicit() -> None:
    request = QueryRequest(question="What does the document say?", document_id="doc-123")
    answer = QueryAnswer(
        answer="It describes the agreed scope.",
        citations=(Citation(document_id="doc-123", filename="notes.pdf", location="page 1"),),
    )

    assert request.document_id == answer.citations[0].document_id
    assert answer.insufficient_context is False
