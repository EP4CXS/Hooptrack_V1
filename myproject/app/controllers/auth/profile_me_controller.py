from app.services.auth.profile_me_service import get_me_payload


def profile_me_action(user):
    return get_me_payload(user)
