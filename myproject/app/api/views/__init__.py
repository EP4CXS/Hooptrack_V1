"""
API views package.

Contains DRF views, view sets, and generic views for the REST API.
Organized by domain in subfolders: auth/, admin/, user/
"""

# Import API views for convenience
# from core.api.views.auth.login_api import LoginAPIView

from .chatbot_views import ChatbotRequestView

__all__ = ["ChatbotRequestView"]
