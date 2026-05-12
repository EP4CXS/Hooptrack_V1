from rest_framework_simplejwt.tokens import RefreshToken


def logout_user(payload):
    refresh_token = payload.get("refresh")
    if not refresh_token:
        return {"success": False, "message": "refresh token is required"}, 400

    token = RefreshToken(refresh_token)
    token.blacklist()
    return {"success": True, "message": "Logged out"}, 200
