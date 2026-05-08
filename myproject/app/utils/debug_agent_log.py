"""Session 66881e: NDJSON debug lines to myproject + workspace root, and stderr."""

from __future__ import annotations

import json
import sys
import time
from typing import Any

from django.conf import settings


def agent_debug_log(
    *,
    hypothesis_id: str,
    message: str,
    data: dict[str, Any] | None = None,
    location: str | None = None,
    run_id: str = "verify",
) -> None:
    line: dict[str, Any] = {
        "sessionId": "66881e",
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000),
    }
    if location:
        line["location"] = location
    text = json.dumps(line) + "\n"
    print(f"DEBUG66881E:{text.rstrip()}", file=sys.stderr, flush=True)
    bases = [settings.BASE_DIR, settings.BASE_DIR.parent.parent]
    for base in bases:
        try:
            with open(base / "debug-66881e.log", "a", encoding="utf-8") as f:
                f.write(text)
        except OSError as exc:
            print(f"DEBUG66881E:log_write_failed:{base}:{exc!s}", file=sys.stderr, flush=True)
