from rest_framework.serializers import ValidationError

from app.controllers.basketball_controller import BasketballController
from app.services.prediction_service import PredictionAIService


def prediction_generate_ai_action_service(*, matchup_id, bracket_id):
    resolved = BasketballController.resolve_matchup(matchup_id=matchup_id, bracket_id=bracket_id)
    matchup = resolved.matchup
    if not matchup.team1 or not matchup.team2:
        raise ValidationError({"matchup": "Matchup must have both teams set before prediction."})
    return PredictionAIService.predict_match(matchup)
