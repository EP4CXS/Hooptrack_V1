from app.services.basketball.bracket_generator_service import bracket_generator_action_service


def bracket_generator_action(payload):
    return bracket_generator_action_service(payload)
