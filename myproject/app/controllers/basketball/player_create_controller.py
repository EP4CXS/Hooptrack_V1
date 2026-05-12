from app.services.basketball.player_create_service import player_create_action_service


def player_create_action(validated_data):
    return player_create_action_service(validated_data)
