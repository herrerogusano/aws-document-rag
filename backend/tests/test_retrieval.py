import pytest

from aws_document_rag.retrieval import owner_retrieval_filter, retrieval_configuration


def test_retrieval_filter_is_exactly_owner_scoped() -> None:
    owner_a = owner_retrieval_filter("owner-a")
    owner_b = owner_retrieval_filter("owner-b")
    assert owner_a == {"equals": {"key": "owner_sub", "value": "owner-a"}}
    assert owner_b != owner_a


def test_unfiltered_retrieval_cannot_be_constructed() -> None:
    with pytest.raises(ValueError):
        owner_retrieval_filter("")


def test_user_a_configuration_cannot_retrieve_user_b_document() -> None:
    documents = [
        {"document_id": "doc-a", "owner_sub": "owner-a"},
        {"document_id": "doc-b", "owner_sub": "owner-b"},
    ]
    configuration = retrieval_configuration("owner-a", number_of_results=3)
    owner = configuration["vectorSearchConfiguration"]["filter"]["equals"]["value"]
    visible = [document for document in documents if document["owner_sub"] == owner]

    assert [document["document_id"] for document in visible] == ["doc-a"]


def test_retrieval_result_count_is_bounded() -> None:
    with pytest.raises(ValueError):
        retrieval_configuration("owner-a", number_of_results=6)


def test_document_filter_can_only_narrow_owner_scope() -> None:
    configuration = retrieval_configuration("owner-a", document_id="doc-a")
    filters = configuration["vectorSearchConfiguration"]["filter"]["andAll"]
    assert filters == [
        {"equals": {"key": "owner_sub", "value": "owner-a"}},
        {"equals": {"key": "document_id", "value": "doc-a"}},
    ]
