from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.controllers.auth.register_user_controller import register_user_action
from app.http.requests.auth.register_user_request import RegisterUserRequest


class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        dto = RegisterUserRequest.from_request_data(request.data)
        payload = register_user_action(dto.payload)
        return Response(payload, status=status.HTTP_201_CREATED)
