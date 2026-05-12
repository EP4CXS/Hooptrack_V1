"""
PredictionAIService

Computes team features (win streak, win rate, average height, top players)
and uses Groq (when GROQ_API_KEY is set) to predict the winner of a Matchup.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.db.models import Avg, Count, F, Q, Sum

from app.models.basketball.models import (
    GamePrediction,
    Matchup,
    Player,
    PlayerGameStat,
)
from app.services.basketball_service import BasketballService
from app.services.groq_completion import groq_chat_completion, groq_is_configured

logger = logging.getLogger(__name__)


def _team_in_matchup(team_name: str) -> Q:
    """Q filter matching matchups where team_name is team1 OR team2."""
    return Q(team1=team_name) | Q(team2=team_name)


def _parse_height_cm(value: Any) -> Optional[float]:
    """Best-effort parse of Player.height into centimeters.

    Accepts inputs like ``"206"``, ``"206 cm"``, ``"2.06 m"``, ``"6'8\""``.
    Returns ``None`` when the value can't be interpreted.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        v = float(value)
        return v if v > 0 else None

    raw = str(value).strip().lower()
    if not raw:
        return None

    feet_inches = re.match(r"^\s*(\d+)\s*['\u2019]\s*(\d+(?:\.\d+)?)?\s*[\"\u201d]?\s*$", raw)
    if feet_inches:
        feet = float(feet_inches.group(1))
        inches = float(feet_inches.group(2) or 0)
        return round((feet * 12 + inches) * 2.54, 1)

    number_match = re.search(r"(\d+(?:\.\d+)?)", raw)
    if not number_match:
        return None
    number = float(number_match.group(1))

    if "m" in raw and "cm" not in raw and "mm" not in raw and number < 3:
        return round(number * 100, 1)
    return round(number, 1)


def _round(value: Optional[float], digits: int = 1) -> Optional[float]:
    if value is None:
        return None
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return None


def _extract_json_object(text: str) -> Dict[str, Any]:
    """Best-effort JSON object extraction from model output."""
    raw = (text or "").strip()
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        pass
    # Fallback: grab first {...} block
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return {}
    try:
        parsed = json.loads(m.group(0))
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


class PredictionAIService:
    """Matchup predictions: Groq when ``groq_is_configured()``; otherwise heuristic fallback."""

    @staticmethod
    def compute_team_features(team_name: str) -> Dict[str, Any]:
        """Aggregate the features the AI needs to reason about a team."""
        if not team_name:
            return {
                "name": team_name or "",
                "win_streak": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "avg_height_cm": None,
                "tallest_player_cm": None,
                "roster_size": 0,
                "top_players": [],
            }

        recent_list = list(
            Matchup.objects.filter(status="completed")
            .filter(winner__isnull=False)
            .filter(_team_in_matchup(team_name))
            .select_related("bracket")
            .order_by("-bracket__created_at", "-round", "-match_number")[:25]
        )

        win_streak = 0
        wins = 0
        losses = 0
        for match in recent_list[:10]:
            if match.winner == team_name:
                wins += 1
            else:
                losses += 1
        for match in recent_list:
            if match.winner == team_name:
                win_streak += 1
            else:
                break

        played = wins + losses
        win_rate = round(wins / played, 3) if played else 0.0

        roster = list(Player.objects.filter(team__name=team_name))
        heights = [h for h in (_parse_height_cm(p.height) for p in roster) if h is not None]
        avg_height_cm = _round(sum(heights) / len(heights)) if heights else None
        tallest_player_cm = _round(max(heights)) if heights else None

        team_stats_qs = PlayerGameStat.objects.filter(team_name=team_name)
        team_box = team_stats_qs.aggregate(
            team_ppg=Avg("points"),
            team_apg=Avg("assists"),
            team_rpg=Avg(F("oreb") + F("dreb")),
            team_total_fgm2=Sum("fgm2"),
            team_total_fga2=Sum("fga2"),
            team_total_fgm3=Sum("fgm3"),
            team_total_fga3=Sum("fga3"),
            team_total_ftm=Sum("ftm"),
            team_total_fta=Sum("fta"),
        )
        total_made = (team_box.get("team_total_fgm2") or 0) + (team_box.get("team_total_fgm3") or 0)
        total_attempt = (team_box.get("team_total_fga2") or 0) + (team_box.get("team_total_fga3") or 0)
        team_fg_pct = round((total_made / total_attempt) * 100, 1) if total_attempt else 0.0
        team_ft_pct = round(((team_box.get("team_total_ftm") or 0) / (team_box.get("team_total_fta") or 0)) * 100, 1) if (team_box.get("team_total_fta") or 0) else 0.0

        top_players = (
            team_stats_qs
            .values("player_id", "player__name", "player__jersey_number", "player__position")
            .annotate(
                games_played=Count("id"),
                ppg=Avg("points"),
                rpg=Avg(F("oreb") + F("dreb")),
                apg=Avg("assists"),
                fgm=Sum(F("fgm2") + F("fgm3")),
                fga=Sum(F("fga2") + F("fga3")),
            )
            .order_by("-ppg")[:3]
        )

        player_profiles = []
        for player in roster:
            per_player = team_stats_qs.filter(player=player).aggregate(
                games_played=Count("id"),
                ppg=Avg("points"),
                apg=Avg("assists"),
                rpg=Avg(F("oreb") + F("dreb")),
            )
            player_profiles.append(
                {
                    "name": player.name,
                    "position": player.position or "",
                    "jersey_number": player.jersey_number or "",
                    "height_cm": _parse_height_cm(player.height),
                    "games_played": per_player.get("games_played") or 0,
                    "ppg": _round(per_player.get("ppg"), 1) or 0.0,
                    "apg": _round(per_player.get("apg"), 1) or 0.0,
                    "rpg": _round(per_player.get("rpg"), 1) or 0.0,
                }
            )
        # Keep prompt payload small/fast: include only the most impactful players.
        player_profiles = sorted(
            player_profiles,
            key=lambda p: (p.get("ppg") or 0.0, p.get("games_played") or 0),
            reverse=True,
        )[:8]

        top_players_payload: List[Dict[str, Any]] = []
        for row in top_players:
            fgm = row.get("fgm") or 0
            fga = row.get("fga") or 0
            fg_pct = round((fgm / fga) * 100, 1) if fga else 0.0
            top_players_payload.append(
                {
                    "name": row.get("player__name") or "",
                    "jersey_number": row.get("player__jersey_number") or "",
                    "position": row.get("player__position") or "",
                    "games_played": row.get("games_played") or 0,
                    "ppg": _round(row.get("ppg"), 1) or 0.0,
                    "rpg": _round(row.get("rpg"), 1) or 0.0,
                    "apg": _round(row.get("apg"), 1) or 0.0,
                    "fg_pct": fg_pct,
                }
            )

        return {
            "name": team_name,
            "win_streak": win_streak,
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
            "avg_height_cm": avg_height_cm,
            "tallest_player_cm": tallest_player_cm,
            "roster_size": len(roster),
            "team_ppg": _round(team_box.get("team_ppg"), 1) or 0.0,
            "team_apg": _round(team_box.get("team_apg"), 1) or 0.0,
            "team_rpg": _round(team_box.get("team_rpg"), 1) or 0.0,
            "team_fg_pct": team_fg_pct,
            "team_ft_pct": team_ft_pct,
            "top_players": top_players_payload,
            "player_profiles": player_profiles,
        }

    @staticmethod
    def _build_prompt(team1_features: Dict[str, Any], team2_features: Dict[str, Any]) -> str:
        payload = {"team1": team1_features, "team2": team2_features}
        return (
            "You are a professional basketball analyst. Predict the winner of an upcoming game between "
            f"{team1_features['name']} and {team2_features['name']}.\n\n"
            "Use the following weighting when reasoning:\n"
            "- Team-level form and efficiency (win streak, win rate, team PPG/APG/RPG, FG%/FT%): 45%\n"
            "- Individual player impact (top players and full player_profiles): 40%\n"
            "- Size profile (average/tallest height and lineup height distribution): 15%\n\n"
            f"Inputs (JSON):\n{json.dumps(payload, ensure_ascii=False)}\n\n"
            "Respond with ONLY a single JSON object, no prose, in this exact shape:\n"
            "{\n"
            f"  \"predicted_winner\": \"{team1_features['name']}\" or \"{team2_features['name']}\",\n"
            "  \"confidence\": <integer between 50 and 95>,\n"
            "  \"reasoning\": \"<two or three concise sentences explaining the pick>\"\n"
            "}"
        )

    @staticmethod
    def _call_groq(prompt: str) -> Dict[str, Any]:
        """Call Groq chat completions and return a parsed prediction dict."""
        model = getattr(
            settings,
            "GROQ_PREDICTION_MODEL",
            getattr(settings, "GROQ_MODEL", "openai/gpt-oss-20b"),
        )
        timeout = int(getattr(settings, "GROQ_TIMEOUT_SECONDS", 90))
        messages = [
            {
                "role": "system",
                "content": (
                    "You return ONLY one valid JSON object matching the user's schema. "
                    "No markdown, no code fences, no commentary."
                ),
            },
            {"role": "user", "content": prompt},
        ]
        try:
            out = groq_chat_completion(
                messages,
                model=model,
                temperature=0.2,
                response_format={"type": "json_object"},
                timeout=timeout,
            )
        except Exception as first_exc:
            logger.warning("Groq json_object mode failed (%s); retrying without response_format", first_exc)
            out = groq_chat_completion(
                messages,
                model=model,
                temperature=0.15,
                response_format=None,
                timeout=timeout,
            )
        parsed = _extract_json_object(out["content"])
        if parsed:
            return parsed
        logger.warning("Groq returned non-JSON. model=%s text=%r", model, (out.get("content") or "")[:500])
        raise ValueError("Groq returned non-JSON prediction output")

    @staticmethod
    def _fallback_prediction(
        team1_features: Dict[str, Any],
        team2_features: Dict[str, Any],
        reason_suffix: str = "",
    ) -> Dict[str, Any]:
        score1 = (
            (team1_features.get("win_streak") or 0) * 4
            + (team1_features.get("win_rate") or 0) * 30
            + sum((p.get("ppg") or 0) for p in team1_features.get("top_players") or [])
            + ((team1_features.get("avg_height_cm") or 0) * 0.05)
        )
        score2 = (
            (team2_features.get("win_streak") or 0) * 4
            + (team2_features.get("win_rate") or 0) * 30
            + sum((p.get("ppg") or 0) for p in team2_features.get("top_players") or [])
            + ((team2_features.get("avg_height_cm") or 0) * 0.05)
        )
        if score1 == score2:
            winner = team1_features["name"]
            confidence = 50
        else:
            winner = team1_features["name"] if score1 > score2 else team2_features["name"]
            spread = abs(score1 - score2)
            total = max(score1 + score2, 1)
            confidence = max(50, min(90, int(50 + (spread / total) * 100)))
        reasoning = (
            f"Heuristic fallback: {winner} edges out based on combined win streak, top scorer output, "
            f"and roster size/height. {reason_suffix}"
        ).strip()
        return {
            "predicted_winner": winner,
            "confidence": confidence,
            "reasoning": reasoning,
        }

    @staticmethod
    def _validate_prediction(
        raw: Dict[str, Any],
        team1_name: str,
        team2_name: str,
    ) -> Optional[Dict[str, Any]]:
        if not isinstance(raw, dict):
            return None
        winner = str(raw.get("predicted_winner") or "").strip()
        if winner not in {team1_name, team2_name}:
            lower = winner.lower()
            if lower == (team1_name or "").lower():
                winner = team1_name
            elif lower == (team2_name or "").lower():
                winner = team2_name
            else:
                return None
        try:
            confidence = int(round(float(raw.get("confidence", 0))))
        except (TypeError, ValueError):
            confidence = 0
        confidence = max(0, min(100, confidence))
        reasoning = str(raw.get("reasoning") or "").strip()
        return {
            "predicted_winner": winner,
            "confidence": confidence,
            "reasoning": reasoning,
        }

    @staticmethod
    def predict_match(matchup: Matchup) -> GamePrediction:
        team1 = matchup.team1 or ""
        team2 = matchup.team2 or ""
        if not team1 or not team2:
            raise ValueError("Matchup must have both teams set before prediction.")

        features1 = PredictionAIService.compute_team_features(team1)
        features2 = PredictionAIService.compute_team_features(team2)
        prompt = PredictionAIService._build_prompt(features1, features2)
        use_groq = groq_is_configured()
        if use_groq:
            model_name = getattr(
                settings,
                "GROQ_PREDICTION_MODEL",
                getattr(settings, "GROQ_MODEL", "openai/gpt-oss-20b"),
            )
        else:
            model_name = "heuristic-only"

        prediction_data: Optional[Dict[str, Any]] = None
        if use_groq:
            try:
                raw = PredictionAIService._call_groq(prompt)
                prediction_data = PredictionAIService._validate_prediction(raw, team1, team2)
                if prediction_data is None:
                    logger.warning("AI returned invalid prediction payload: %r", raw)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Groq prediction failed, falling back to heuristic: %s", exc)
                prediction_data = None

        if prediction_data is None:
            prediction_data = PredictionAIService._fallback_prediction(
                features1,
                features2,
                reason_suffix="(AI provider unavailable or invalid output)",
            )
            model_name = f"{model_name} (fallback)"

        factors = {"team1": features1, "team2": features2}
        return BasketballService.upsert_prediction(
            matchup.matchup_id,
            prediction_data["predicted_winner"],
            prediction_data["confidence"],
            matchup=matchup,
            reasoning=prediction_data.get("reasoning", ""),
            factors=factors,
            generated_by="ai",
            model_name=model_name,
        )

