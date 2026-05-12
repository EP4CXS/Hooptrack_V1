from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.controllers.chatbot.chatbot_request_controller import chatbot_request_action_controller
from app.http.requests.chatbot.chatbot_request_request import ChatbotRequestRequest


class ChatbotRequestActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        dto = ChatbotRequestRequest.from_request_data(request.data)
        result = chatbot_request_action_controller(
            message=dto.message, history=dto.history, user=request.user
        )
        return Response({"success": True, "data": result}, status=status.HTTP_200_OK)
