import pytest

from aws_document_rag.retrieval import owner_retrieval_filter


def test_retrieval_filter_is_exactly_owner_scoped() -> None:
    assert owner_retrieval_filter("owner-a") == {"equals": {"key": "owner_sub", "value": "owner-a"}}


def test_unfiltered_retrieval_cannot_be_constructed() -> None:
    with pytest.raises(ValueError):
        owner_retrieval_filter("")
