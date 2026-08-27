"""Provider-neutral contracts shared by future API and RAG adapters."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class DocumentStatus(StrEnum):
    """Safe, application-level document lifecycle states."""

    PENDING_UPLOAD = "PENDING_UPLOAD"
    UPLOADED = "UPLOADED"
    INGESTING = "INGESTING"
    READY = "READY"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class DocumentRecord:
    """Metadata visible to an owner; no S3 key or provider identifiers are exposed."""

    document_id: str
    filename: str
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime
    error_code: str | None = None


@dataclass(frozen=True, slots=True)
class QueryRequest:
    """A bounded question, optionally limited to one document."""

    question: str
    document_id: str | None = None


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    """Normalized retrieval result retained server-side before answer generation."""

    document_id: str
    filename: str
    text: str
    location: str | None = None


@dataclass(frozen=True, slots=True)
class Citation:
    """A safe reference to a retrieved source."""

    document_id: str
    filename: str
    location: str | None = None


@dataclass(frozen=True, slots=True)
class QueryAnswer:
    """A grounded answer and only the citations used to support it."""

    answer: str
    citations: tuple[Citation, ...]
    insufficient_context: bool = False
