"""Mandatory ownership filter for every knowledge-base retrieval."""

from __future__ import annotations

from typing import Any


def owner_retrieval_filter(owner_sub: str) -> dict[str, Any]:
    if not owner_sub:
        raise ValueError("Authenticated owner is required for retrieval")
    return {"equals": {"key": "owner_sub", "value": owner_sub}}


def retrieval_configuration(owner_sub: str, number_of_results: int = 5) -> dict[str, Any]:
    if not 1 <= number_of_results <= 5:
        raise ValueError("Retrieval result count must remain bounded")
    return {
        "vectorSearchConfiguration": {
            "numberOfResults": number_of_results,
            "filter": owner_retrieval_filter(owner_sub),
        }
    }
