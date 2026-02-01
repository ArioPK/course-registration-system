# backend/app/utils/current_term.py

from __future__ import annotations

import os


def get_current_term() -> str:
    """
    Returns the current term used for term-scoped operations (enroll/drop/schedule).
    """
    return os.getenv("CURRENT_TERM", "1")