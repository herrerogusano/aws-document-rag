"""Mandatory ownership filter for every knowledge-base retrieval."""

from __future__ import annotations

from typing import Any


def owner_retrieval_filter(owner_sub: str) -> dict[str, Any]:
    if not owner_sub:
        raise ValueError("Authenticated owner is required for retrieval")
    return {"equals": {"key": "owner_sub", "value": owner_sub}}
