from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from app.models.basketball.models import Bracket, GamePrediction, Matchup, Player, Team, TeamStanding


class BasketballService:
    @staticmethod
    def extract_team_name(team_value):
        if isinstance(team_value, dict):
            return team_value.get("name")
        return team_value

    @staticmethod
    def normalize_bracket_payload(data):
        return {
            "name": data.get("name"),
            "format": data.get("format"),
            "teams": data.get("teams", []),
            "current_round": data.get("currentRound", 1),
            "total_rounds": data.get("totalRounds", 1),
            "status": data.get("status", "active"),
            "start_date": data.get("startDate"),
            "location": data.get("location"),
            "include_bronze_match": data.get("includeBronzeMatch", False),
            "include_quarter_finals": data.get("includeQuarterFinals", False),
            "round_robin_config": data.get("roundRobinConfig"),
            "final_rankings": data.get("finalRankings"),
        }

    @staticmethod
    def normalize_matchup_payload(matchup):
        return {
            "matchup_id": matchup.get("id"),
            "team1": matchup.get("team1"),
            "team2": matchup.get("team2"),
            "winner": matchup.get("winner"),
            "score1": matchup.get("score1"),
            "score2": matchup.get("score2"),
            "round": matchup.get("round", 1),
            "match_number": matchup.get("matchNumber", 1),
            "status": matchup.get("status", "pending"),
            "stage": matchup.get("stage", "group"),
            "bracket_type": matchup.get("bracketType"),
            "bracket_group": matchup.get("bracketGroup"),
            "scheduled_date": matchup.get("scheduledDate"),
            "scheduled_time": matchup.get("scheduledTime"),
            "venue": matchup.get("venue"),
            "is_bye": matchup.get("isBye", False),
            "is_bronze_match": matchup.get("isBronzeMatch", False),
            "next_matchup_id": matchup.get("nextMatchId"),
            "loser_next_matchup_id": matchup.get("loserNextMatchId"),
        }

    @staticmethod
    def normalize_standing_payload(standing):
        return {
            "team": standing.get("team"),
            "wins": standing.get("wins", 0),
            "losses": standing.get("losses", 0),
            "points": standing.get("points", 0),
            "matches_played": standing.get("matchesPlayed", 0),
            "bracket_group": standing.get("bracketGroup"),
        }

    @staticmethod
    def create_player(data):
        team_name = BasketballService.extract_team_name(data.pop("team", None))
        owner = data.get("created_by")
        if owner and not (data.get("municipality") or "").strip():
            profile = getattr(owner, "profile", None)
            if profile and (profile.municipality or "").strip():
                data["municipality"] = profile.municipality.strip()
        team_qs = Team.objects.filter(name=team_name) if team_name else Team.objects.none()
        if owner:
            team_qs = team_qs.filter(created_by=owner)
        team = team_qs.first() if team_name else None
        return Player.objects.create(team=team, **data)

    @staticmethod
    def update_player(instance, data):
        had_team = "team" in data
        team_name = BasketballService.extract_team_name(data.pop("team", None))
        if had_team or team_name is not None:
            team_qs = Team.objects.filter(name=team_name) if team_name else Team.objects.none()
            if instance.created_by_id:
                team_qs = team_qs.filter(created_by_id=instance.created_by_id)
            instance.team = team_qs.first() if team_name else None
        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def create_bracket_with_relations(data):
        matchups = data.pop("matchups", [])
        standings = data.pop("standings", [])
        bracket = Bracket.objects.create(**BasketballService.normalize_bracket_payload(data))
        for matchup in matchups:
            Matchup.objects.create(bracket=bracket, **BasketballService.normalize_matchup_payload(matchup))
        for standing in standings:
            TeamStanding.objects.create(bracket=bracket, **BasketballService.normalize_standing_payload(standing))
        return bracket

    @staticmethod
    @transaction.atomic
    def replace_bracket_relations(bracket, matchups=None, standings=None):
        if matchups is not None:
            bracket.matchup_set.all().delete()
            for matchup in matchups:
                Matchup.objects.create(bracket=bracket, **BasketballService.normalize_matchup_payload(matchup))
        if standings is not None:
            bracket.teamstanding_set.all().delete()
            for standing in standings:
                TeamStanding.objects.create(bracket=bracket, **BasketballService.normalize_standing_payload(standing))
        return bracket

    @staticmethod
    def upsert_prediction(matchup_id, predicted_winner, confidence, *, matchup=None, bracket_id=None, **extra):
        """Create or update the prediction for a matchup.

        Pass ``matchup`` when already resolved, or ``bracket_id`` with ``matchup_id`` (unique per bracket).
        Optional fields supported via ``extra``: ``reasoning``, ``factors``,
        ``generated_by``, ``model_name``. Unknown keys are ignored.
        """
        if matchup is None:
            if bracket_id is not None and str(bracket_id).strip() != "":
                matchup = get_object_or_404(Matchup, bracket_id=bracket_id, matchup_id=matchup_id)
            else:
                qs = Matchup.objects.filter(matchup_id=matchup_id)
                n = qs.count()
                if n == 0:
                    matchup = get_object_or_404(Matchup, matchup_id=matchup_id)
                elif n == 1:
                    matchup = qs.first()
                else:
                    raise ValidationError(
                        {"matchupId": "This matchup id exists in multiple brackets; include bracketId."}
                    )
        defaults = {
            "predicted_winner": predicted_winner,
            "confidence": confidence,
        }
        for key in ("reasoning", "factors", "generated_by", "model_name"):
            if key in extra and extra[key] is not None:
                defaults[key] = extra[key]
        prediction, _ = GamePrediction.objects.update_or_create(
            matchup=matchup,
            defaults=defaults,
        )
        return prediction
