"""OpenAI-compatible Groq chat completions (used by chatbot and matchup predictions)."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from django.conf import settings
from urllib import error, request

logger = logging.getLogger(__name__)


def groq_is_configured() -> bool:
    """True when GROQ_API_KEY is set (chatbot + matchup predictions use Groq)."""
    return bool((getattr(settings, "GROQ_API_KEY", "") or "").strip())


def groq_chat_completion(
    messages: List[Dict[str, Any]],
    *,
    model: Optional[str] = None,
    temperature: float = 0.3,
    response_format: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = None,
) -> Dict[str, str]:
    """
    POST to Groq chat completions API.

    Returns:
        {"content": "<assistant text>", "model": "<model id>"}

    Raises on missing key, HTTP errors, or empty assistant content.
    """
    api_key = (getattr(settings, "GROQ_API_KEY", "") or "").strip()
    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured")

    resolved_model = model or getattr(settings, "GROQ_MODEL", "openai/gpt-oss-20b")
    resolved_timeout = int(
        timeout if timeout is not None else getattr(settings, "GROQ_TIMEOUT_SECONDS", 60)
    )
    url = getattr(
        settings,
        "GROQ_BASE_URL",
        "https://api.groq.com/openai/v1/chat/completions",
    )

    payload: Dict[str, Any] = {
        "model": resolved_model,
        "messages": messages,
        "temperature": temperature,
    }
    if response_format is not None:
        payload["response_format"] = response_format

    req = request.Request(
        url=url,
        method="POST",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # Groq is fronted by Cloudflare; some environments get blocked without
            # a recognizable User-Agent header (seen as HTTP 403 / error code 1010).
            "User-Agent": "HoopTrack/1.0 (Django chatbot)",
            "Accept": "application/json",
        },
    )

    try:
        with request.urlopen(req, timeout=resolved_timeout) as res:
            body = res.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = ""
        try:
            if exc.fp:
                detail = exc.read().decode("utf-8", errors="replace")
        except Exception:
            detail = ""
        # Include a useful snippet of the response body for debugging.
        logger.warning(
            "Groq HTTP %s: %s",
            exc.code,
            (detail or exc.reason or "no detail")[:1000],
        )
        raise

    data = json.loads(body) if body else {}
    content = (
        (data.get("choices") or [{}])[0]
        .get("message", {})
        .get("content", "")
        or ""
    ).strip()
    if not content:
        raise ValueError("Groq returned an empty assistant message")
    return {"content": content, "model": resolved_model}
