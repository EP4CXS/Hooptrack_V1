from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from app.controllers.auth.logout_user_controller import logout_user_action
from app.http.requests.auth.logout_user_request import LogoutUserRequest


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_user_view(request):
    dto = LogoutUserRequest.from_request_data(request.data)
    payload, code = logout_user_action(dto.payload)
    return Response(payload, status=code)
