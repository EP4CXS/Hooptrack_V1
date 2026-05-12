from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
