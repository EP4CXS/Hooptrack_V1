from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from app.controllers.auth.locations_regions_controller import locations_regions_action


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def locations_regions_view(_request):
    return Response(locations_regions_action())
