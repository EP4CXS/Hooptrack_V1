from rest_framework_simplejwt.tokens import RefreshToken

from app.api.serializers.auth_serializers import RegisterSerializer, UserSerializer


def register_user(payload):
    serializer = RegisterSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    return {
        "success": True,
        "message": "Registration successful",
        "data": {
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
    }
