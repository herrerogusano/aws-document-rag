"""Owner-scoped document request validation for the Phase 3 API."""

from pathlib import PurePosixPath
from uuid import uuid4

ALLOWED_EXTENSIONS = {"pdf", "txt", "md"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


def create_document_key(owner_sub: str, filename: str) -> tuple[str, str]:
    """Return a server-owned document id and private S3 key."""
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_EXTENSIONS or PurePosixPath(filename).name != filename:
        raise ValueError("Unsupported file type")
    document_id = str(uuid4())
    return document_id, f"users/{owner_sub}/documents/{document_id}/source.{extension}"


def validate_upload_size(size_bytes: int) -> None:
    if not 0 < size_bytes <= MAX_UPLOAD_BYTES:
        raise ValueError("File size is outside the allowed limit")
