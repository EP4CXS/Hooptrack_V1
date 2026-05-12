from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from app.controllers.auth.profile_me_controller import profile_me_action


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def profile_me_view(request):
    return Response(profile_me_action(request.user), status=200)
