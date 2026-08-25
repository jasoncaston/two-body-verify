"""Claims file loading and validation."""

import json
from pathlib import Path
from typing import Any, Dict, List


def load_claims(path: Path) -> List[Dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"claims file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"claims file is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValueError("claims file must be an object with version 1")
    claims = payload.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ValueError("claims file must contain at least one claim")
    seen = set()
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            raise ValueError(f"claim {index + 1} must be an object")
        claim_id = claim.get("id")
        if not isinstance(claim_id, str) or not claim_id:
            raise ValueError(f"claim {index + 1} must have a non-empty id")
        if claim_id in seen:
            raise ValueError(f"duplicate claim id: {claim_id}")
        seen.add(claim_id)
        if not isinstance(claim.get("statement"), str) or not claim["statement"]:
            raise ValueError(f"claim {claim_id} must have a non-empty statement")
        checks = claim.get("checks")
        if not isinstance(checks, list) or not checks:
            raise ValueError(f"claim {claim_id} must contain at least one check")
        if not all(isinstance(check, dict) for check in checks):
            raise ValueError(f"claim {claim_id} checks must be objects")
    return claims
