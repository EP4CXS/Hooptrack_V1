"""
Root API URL routing.

Includes all domain-specific API endpoints with prefix /api/.
"""

from django.urls import include, path

urlpatterns = [
    path("auth/", include("app.api.urls.auth_urls")),
    path("basketball/", include("app.api.urls.basketball_urls")),
    path("chatbot/", include("app.api.urls.chatbot_urls")),
]
