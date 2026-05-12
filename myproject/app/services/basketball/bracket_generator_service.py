from app.services.basketball_service import BasketballService


def bracket_generator_action_service(payload):
    return BasketballService.create_bracket_with_relations(payload)
