from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from django.shortcuts import get_object_or_404
from rest_framework.serializers import ValidationError

from app.models.basketball.models import Matchup
from app.services.basketball_service import BasketballService
from app.services.prediction_service import PredictionAIService


@dataclass(frozen=True)
class ResolvedMatchup:
    matchup: Matchup
    bracket_id: Optional[str]
    matchup_id: str


class BasketballController:
    """Orchestrates basketball domain operations for API/views."""

    @staticmethod
    def create_player(validated_data: Dict[str, Any]):
        return BasketballService.create_player(validated_data)

    @staticmethod
    def update_player(instance, validated_data: Dict[str, Any]):
        return BasketballService.update_player(instance, validated_data)

    @staticmethod
    def create_bracket_with_relations(payload: Dict[str, Any]):
        return BasketballService.create_bracket_with_relations(payload)

    @staticmethod
    def update_bracket_with_relations(instance, payload: Dict[str, Any]):
        normalized = BasketballService.normalize_bracket_payload(payload)
        for key, value in normalized.items():
            if value is not None:
                setattr(instance, key, value)
        instance.save()
        BasketballService.replace_bracket_relations(
            instance,
            matchups=payload.get("matchups"),
            standings=payload.get("standings"),
        )
        return instance

    @staticmethod
    def upsert_prediction(
        matchup_id: str,
        predicted_winner: str,
        confidence: Any,
        *,
        bracket_id: Optional[str] = None,
        generated_by: str = "user",
        reasoning: Optional[str] = None,
        factors: Optional[dict] = None,
        model_name: Optional[str] = None,
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

    @staticmethod
    def resolve_matchup(*, matchup_id: str, bracket_id: Optional[str]) -> ResolvedMatchup:
        """Resolve matchup uniquely, matching existing API behavior.

        - If bracket_id is provided, resolve within that bracket.
        - Otherwise allow globally unique matchup_id, but error if ambiguous.
        """
        if not matchup_id:
            raise ValidationError({"matchupId": "matchupId is required"})

        if bracket_id is not None and str(bracket_id).strip() != "":
            matchup = get_object_or_404(Matchup, bracket_id=bracket_id, matchup_id=matchup_id)
            return ResolvedMatchup(matchup=matchup, bracket_id=str(bracket_id), matchup_id=str(matchup_id))

        qs = Matchup.objects.filter(matchup_id=matchup_id)
        n = qs.count()
        if n == 0:
            matchup = get_object_or_404(Matchup, matchup_id=matchup_id)  # raises 404
        elif n == 1:
            matchup = qs.first()
        else:
            raise ValidationError(
                {"bracketId": "This matchup id exists in multiple brackets; send bracketId from the active bracket."}
            )
        return ResolvedMatchup(matchup=matchup, bracket_id=None, matchup_id=str(matchup_id))

    @staticmethod
    def generate_ai_prediction(*, matchup_id: str, bracket_id: Optional[str]):
        resolved = BasketballController.resolve_matchup(matchup_id=matchup_id, bracket_id=bracket_id)
        matchup = resolved.matchup

        if not matchup.team1 or not matchup.team2:
            raise ValidationError({"matchup": "Matchup must have both teams set before prediction."})

        return PredictionAIService.predict_match(matchup)

