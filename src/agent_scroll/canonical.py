"""RFC 8785 JCS encoding + sha256:hex hash string."""

from __future__ import annotations

import hashlib
from typing import Any

import jcs as _jcs


def canonical(value: Any) -> bytes:
    return _jcs.canonicalize(value)


def hash_canonical(value: Any) -> str:
    digest = hashlib.sha256(canonical(value)).hexdigest()
    return f"sha256:{digest}"
