from app.services.basketball_service import BasketballService


def prediction_upsert_action_service(
    matchup_id,
    predicted_winner,
    confidence,
    *,
    bracket_id=None,
    generated_by="user",
    reasoning=None,
    factors=None,
    model_name=None,
):
    return BasketballService.upsert_prediction(
        matchup_id,
        predicted_winner,
        confidence,
        bracket_id=bracket_id,
        generated_by=generated_by,
        reasoning=reasoning,
        factors=factors,
        model_name=model_name,
    )
