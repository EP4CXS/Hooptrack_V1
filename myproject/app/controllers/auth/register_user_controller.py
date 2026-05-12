from app.services.auth.register_user_service import register_user


def register_user_action(payload):
    return register_user(payload)
