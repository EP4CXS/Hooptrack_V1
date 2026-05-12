from app.services.auth.logout_user_service import logout_user


def logout_user_action(payload):
    return logout_user(payload)
