from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional

from rest_framework.serializers import ValidationError


def _required_str(field: str, value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValidationError({field: f"{field} is required"})
    return text


@dataclass(frozen=True)
class ChatbotRequest:
    message: str
    history: Optional[List[dict]]

    @staticmethod
    def from_request_data(data: Any) -> "ChatbotRequest":
        getter = getattr(data, "get", lambda _k, _d=None: None)
        message = _required_str("message", getter("message"))
        if len(message) > 2000:
            raise ValidationError({"message": "message is too long (max 2000 chars)"})

        history_raw = getter("history")
        if history_raw is None:
            history = None
        elif isinstance(history_raw, list):
            history = [item for item in history_raw if isinstance(item, dict)]
        else:
            raise ValidationError({"history": "history must be an array"})

        return ChatbotRequest(message=message, history=history)
