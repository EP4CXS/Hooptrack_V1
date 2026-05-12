from app.services.basketball.bracket_update_service import bracket_update_action_service


def bracket_update_action(instance, payload):
    return bracket_update_action_service(instance, payload)
