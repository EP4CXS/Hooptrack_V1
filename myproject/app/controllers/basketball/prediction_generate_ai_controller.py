from app.services.basketball.prediction_generate_ai_service import prediction_generate_ai_action_service


def prediction_generate_ai_action(*, matchup_id, bracket_id=None):
    return prediction_generate_ai_action_service(matchup_id=matchup_id, bracket_id=bracket_id)
