# backend/app/utils/current_term.py

from __future__ import annotations

import os
from backend.app.config.settings import settings


def get_current_term() -> str:
    """
    Single source of truth for current term.
    Reads env at call-time (important for tests monkeypatching CURRENT_TERM),
    falling back to settings default.
    """
    return os.getenv("CURRENT_TERM", settings.CURRENT_TERM)