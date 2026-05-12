from app.api.serializers.auth_serializers import UserSerializer


def get_me_payload(user):
    return {"success": True, "data": UserSerializer(user).data}
