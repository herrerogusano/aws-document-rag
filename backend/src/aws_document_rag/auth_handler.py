"""Phase 2 protected API handler; API Gateway performs JWT validation first."""

from __future__ import annotations

import json
from typing import Any


def me(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    """Return only the stable owner identifier from validated JWT authorizer claims."""

    claims = event.get("requestContext", {}).get("authorizer", {}).get("jwt", {}).get("claims", {})
    owner_sub = claims.get("sub")
    if not isinstance(owner_sub, str) or not owner_sub:
        return {"statusCode": 401, "body": json.dumps({"message": "Unauthorized"})}

    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": json.dumps({"ownerId": owner_sub}),
    }
