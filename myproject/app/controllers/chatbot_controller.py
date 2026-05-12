from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

from app.services.chatbot_service import ChatbotService

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser


class ChatbotController:
    """Orchestrates chatbot use cases for API layer."""

    @staticmethod
    def request_reply(
        message: str,
        history: Optional[List[dict]] = None,
        user: Optional["AbstractBaseUser"] = None,
    ) -> Dict[str, str]:
        return ChatbotService.ask(message=message, history=history, user=user)
