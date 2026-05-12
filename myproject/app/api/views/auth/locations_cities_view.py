from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from app.controllers.auth.locations_cities_controller import locations_cities_action


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def locations_cities_view(_request, province_id):
    return Response(locations_cities_action(province_id))
