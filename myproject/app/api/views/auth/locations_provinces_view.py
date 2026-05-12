from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from app.controllers.auth.locations_provinces_controller import locations_provinces_action


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def locations_provinces_view(_request, region_id):
    return Response(locations_provinces_action(region_id))
