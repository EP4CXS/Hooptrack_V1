from app.services.basketball.player_update_service import player_update_action_service


def player_update_action(instance, validated_data):
    return player_update_action_service(instance, validated_data)
