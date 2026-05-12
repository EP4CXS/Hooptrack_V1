"""
Services package for the Core application.

Service layer containing business logic separated from views.
Services encapsulate complex operations and coordinate between
models, selectors, and other domain components.

Organized by domain:
- auth/:   Authentication and authorization services
- admin/:  Administrative services
- user/:   User management services

Usage pattern:
    from core.services.auth.login_service import LoginService
    result = LoginService.execute(user_data)
"""

# Import services for convenient access
# from core.services.auth.login_service import LoginService
# from core.services.auth.register_service import RegisterService

from .basketball_service import BasketballService
from .chatbot_service import ChatbotService
from .prediction_service import PredictionAIService

__all__ = ["BasketballService", "PredictionAIService", "ChatbotService"]
