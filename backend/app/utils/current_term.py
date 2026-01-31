# backend/app/utils/current_term.py

from __future__ import annotations

import os


def get_current_term() -> str:
    return os.getenv("CURRENT_TERM", "1404-2")  # default to "1404-2" if not provided