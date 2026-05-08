from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from rest_framework.serializers import ValidationError


def _optional_str(v: Any) -> Optional[str]:
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


def _required_str(field: str, v: Any) -> str:
    s = _optional_str(v)
    if not s:
        raise ValidationError({field: f"{field} is required"})
    return s


def _optional_int(v: Any) -> Optional[int]:
    if v is None or (isinstance(v, str) and v.strip() == ""):
        return None
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class GeneratePredictionRequest:
    matchup_id: str
    bracket_id: Optional[str]

    @staticmethod
    def from_request_data(data: Any) -> "GeneratePredictionRequest":
        matchup_id = _required_str("matchupId", getattr(data, "get", lambda _k, _d=None: None)("matchupId"))
        bracket_id = _optional_str(getattr(data, "get", lambda _k, _d=None: None)("bracketId"))
        return GeneratePredictionRequest(matchup_id=matchup_id, bracket_id=bracket_id)


@dataclass(frozen=True)
class UpsertPredictionRequest:
    matchup_id: str
    predicted_winner: str
    confidence: int
    bracket_id: Optional[str]
    generated_by: str

    @staticmethod
    def from_request_data(data: Any) -> "UpsertPredictionRequest":
        getter = getattr(data, "get", lambda _k, _d=None: None)
        matchup_id = _required_str("matchupId", getter("matchupId"))
        predicted_winner = _required_str("predictedWinner", getter("predictedWinner"))
        confidence = _optional_int(getter("confidence"))
        if confidence is None:
            raise ValidationError({"confidence": "confidence must be a number"})
        bracket_id = _optional_str(getter("bracketId"))
        generated_by = _optional_str(getter("generatedBy")) or "user"
        return UpsertPredictionRequest(
            matchup_id=matchup_id,
            predicted_winner=predicted_winner,
            confidence=confidence,
            bracket_id=bracket_id,
            generated_by=generated_by,
        )

