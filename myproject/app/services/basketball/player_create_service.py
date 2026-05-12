from app.services.basketball_service import BasketballService


def player_create_action_service(validated_data):
    return BasketballService.create_player(validated_data)
