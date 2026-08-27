"""Content-free structured events for native Lambda/CloudWatch logs."""

from __future__ import annotations

import json
import logging
from typing import Any

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def request_id(event: dict[str, Any], context: Any) -> str:
    gateway_id = event.get("requestContext", {}).get("requestId")
    lambda_id = getattr(context, "aws_request_id", None)
    return str(gateway_id or lambda_id or "unknown")


def log_event(name: str, event: dict[str, Any], context: Any, **metrics: int | str | bool) -> None:
    """Log allow-listed operational metadata, never request or document content."""
    LOGGER.info(
        json.dumps(
            {"event": name, "requestId": request_id(event, context), **metrics},
            separators=(",", ":"),
            sort_keys=True,
        )
    )
