from rest_framework import permissions
from rest_framework_simplejwt.views import TokenRefreshView


class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
