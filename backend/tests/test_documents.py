import pytest

from aws_document_rag.documents import create_document_key, validate_upload_size


def test_key_is_owner_scoped_and_server_generated() -> None:
    document_id, key = create_document_key("owner-a", "notes.pdf")
    assert key == f"users/owner-a/documents/{document_id}/source.pdf"


@pytest.mark.parametrize("filename", ["../../secret.pdf", "notes.exe", "no-extension"])
def test_invalid_filename_is_rejected(filename: str) -> None:
    with pytest.raises(ValueError):
        create_document_key("owner-a", filename)


def test_size_is_bounded() -> None:
    validate_upload_size(1)
    with pytest.raises(ValueError):
        validate_upload_size(5 * 1024 * 1024 + 1)
