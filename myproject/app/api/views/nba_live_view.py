from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.controllers.basketball.nba_live_controller import nba_live_action_controller


class NbaLiveActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, _request):
        result = nba_live_action_controller()
        return Response({"success": True, "data": result}, status=status.HTTP_200_OK)
