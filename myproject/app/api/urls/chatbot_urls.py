from django.urls import path

from app.api.views.chatbot_views import ChatbotRequestView

urlpatterns = [
    path("request/", ChatbotRequestView.as_view(), name="api-chatbot-request"),
]
