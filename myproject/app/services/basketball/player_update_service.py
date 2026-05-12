from app.services.basketball_service import BasketballService


def player_update_action_service(instance, validated_data):
    return BasketballService.update_player(instance, validated_data)
