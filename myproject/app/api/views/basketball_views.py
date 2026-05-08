from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from app.api.serializers.basketball_serializers import (
    BracketSerializer,
    GameEventSerializer,
    GameSerializer,
    GamePredictionSerializer,
    MatchupSerializer,
    PlayerSerializer,
    TeamSerializer,
)
from app.models.basketball.models import Bracket, Game, GameEvent, GamePrediction, Matchup, Player, PlayerGameStat, Team
from app.controllers.basketball_controller import BasketballController
from app.http.requests.basketball_requests import GeneratePredictionRequest, UpsertPredictionRequest
from app.utils.debug_agent_log import agent_debug_log
from app.utils.responses import success_response


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all().order_by("name")
    serializer_class = TeamSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["conference", "division"]
    search_fields = ["name", "city"]
    pagination_class = None


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.select_related("team").all().order_by("name")
    serializer_class = PlayerSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["position", "team__name"]
    search_fields = ["name", "team__name", "jersey_number"]
    pagination_class = None

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        player = BasketballController.create_player(serializer.validated_data)
        return Response(PlayerSerializer(player).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        player = BasketballController.update_player(instance, serializer.validated_data)
        return Response(PlayerSerializer(player).data, status=status.HTTP_200_OK)


class BracketViewSet(viewsets.ModelViewSet):
    queryset = Bracket.objects.all().prefetch_related("matchup_set", "teamstanding_set")
    serializer_class = BracketSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def create(self, request, *args, **kwargs):
        payload = request.data
        bracket = BasketballController.create_bracket_with_relations(
            {
                **payload,
                "matchups": payload.get("matchups", []),
                "standings": payload.get("standings", []),
            }
        )
        return Response(BracketSerializer(bracket).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        kwargs.pop("partial", False)
        instance = self.get_object()
        payload = request.data
        instance = BasketballController.update_bracket_with_relations(instance, payload)
        return Response(BracketSerializer(instance).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[permissions.AllowAny])
    def predictions(self, request, pk=None):
        predicted_winner = request.data.get("predictedWinner")
        confidence = request.data.get("confidence")
        matchup_id = request.data.get("matchupId")
        bracket_id = request.data.get("bracketId") or pk
        prediction = BasketballService.upsert_prediction(
            matchup_id, predicted_winner, confidence, bracket_id=bracket_id
        )
        return success_response(GamePredictionSerializer(prediction).data, "Prediction saved")


class MatchupViewSet(viewsets.ModelViewSet):
    queryset = Matchup.objects.all().select_related("bracket")
    serializer_class = MatchupSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class GamePredictionViewSet(viewsets.ModelViewSet):
    queryset = GamePrediction.objects.all().select_related("matchup")
    serializer_class = GamePredictionSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def create(self, request, *args, **kwargs):
        dto = UpsertPredictionRequest.from_request_data(request.data)
        prediction = BasketballController.upsert_prediction(
            dto.matchup_id,
            dto.predicted_winner,
            dto.confidence,
            bracket_id=dto.bracket_id,
            generated_by=dto.generated_by,
        )
        return Response(GamePredictionSerializer(prediction).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="generate", permission_classes=[permissions.AllowAny])
    def generate(self, request):
        # #region agent log
        try:
            _keys = sorted(str(k) for k in request.data.keys())
        except Exception as _e:
            _keys = [f"_keys_error:{type(_e).__name__}"]
        agent_debug_log(
            hypothesis_id="0",
            message="generate_entry",
            data={"method": request.method, "path": getattr(request, "path", ""), "data_keys": _keys},
            location="basketball_views.GamePredictionViewSet.generate",
        )
        # #endregion
        dto = GeneratePredictionRequest.from_request_data(request.data)
        matchup_id = dto.matchup_id
        bracket_id = dto.bracket_id
        # #region agent log
        _dup = Matchup.objects.filter(matchup_id=matchup_id).count() if matchup_id else 0
        agent_debug_log(
            hypothesis_id="A",
            message="generate_request",
            data={
                "data_keys": sorted(str(k) for k in request.data.keys()),
                "matchup_id": str(matchup_id),
                "bracket_id_raw": bracket_id,
                "bracket_id_nonempty": bool(bracket_id is not None and str(bracket_id).strip() != ""),
                "matchup_rows_with_this_id": _dup,
            },
            location="basketball_views.GamePredictionViewSet.generate",
        )
        # #endregion
        resolved = BasketballController.resolve_matchup(matchup_id=matchup_id, bracket_id=bracket_id)
        matchup = resolved.matchup
        # #region agent log
        agent_debug_log(
            hypothesis_id="B",
            message="matchup_resolved",
            data={"matchup_pk": matchup.pk, "bracket_id": matchup.bracket_id, "matchup_id": matchup.matchup_id},
            location="basketball_views.GamePredictionViewSet.generate",
        )
        # #endregion
        try:
            prediction = BasketballController.generate_ai_prediction(matchup_id=matchup_id, bracket_id=bracket_id)
        except Exception as exc:
            # #region agent log
            agent_debug_log(
                hypothesis_id="C",
                message="predict_match_exception",
                data={"exc_type": type(exc).__name__, "exc_msg": str(exc)[:500]},
                location="basketball_views.GamePredictionViewSet.generate",
            )
            # #endregion
            raise
        # #region agent log
        agent_debug_log(
            hypothesis_id="C",
            message="generate_ok",
            data={"prediction_id": prediction.pk},
            location="basketball_views.GamePredictionViewSet.generate",
        )
        # #endregion
        return Response(GamePredictionSerializer(prediction).data, status=status.HTTP_200_OK)


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all().select_related("bracket", "matchup").prefetch_related("player_stats", "events")
    serializer_class = GameSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def create(self, request, *args, **kwargs):
        payload = request.data
        bracket_id = payload.get("bracket")
        matchup_ref = payload.get("matchup")
        matchup_obj = None
        if matchup_ref is not None and matchup_ref != "":
            matchup_text = str(matchup_ref).strip()
            if matchup_text.isdigit():
                matchup_obj = Matchup.objects.filter(pk=int(matchup_text)).first()
            else:
                lookup = Matchup.objects.filter(matchup_id=matchup_text)
                if bracket_id:
                    lookup = lookup.filter(bracket_id=bracket_id)
                matchup_obj = lookup.first()
            if matchup_obj is None:
                raise ValidationError({"matchup": f"Invalid matchup reference: {matchup_ref}"})

        game = Game.objects.create(
            bracket_id=bracket_id,
            matchup=matchup_obj,
            team1_name=payload.get("team1Name") or payload.get("team1_name"),
            team2_name=payload.get("team2Name") or payload.get("team2_name"),
            score1=payload.get("score1", 0),
            score2=payload.get("score2", 0),
            quarter=payload.get("quarter", 1),
            clock=payload.get("clock", "12:00"),
            status=payload.get("status", "in-progress"),
        )
        return Response(GameSerializer(game).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[permissions.AllowAny])
    def sync_stats(self, request, pk=None):
        game = self.get_object()
        rows = request.data.get("playerStats", [])
        seen_ids = set()
        for row in rows:
            player_id = row.get("player")
            if not player_id:
                continue
            stat, _ = PlayerGameStat.objects.update_or_create(
                game=game,
                player_id=player_id,
                defaults={
                    "team_name": row.get("teamName") or row.get("team_name") or "",
                    "fgm2": row.get("fgm2", 0),
                    "fga2": row.get("fga2", 0),
                    "fgm3": row.get("fgm3", 0),
                    "fga3": row.get("fga3", 0),
                    "ftm": row.get("ftm", 0),
                    "fta": row.get("fta", 0),
                    "oreb": row.get("oreb", 0),
                    "dreb": row.get("dreb", 0),
                    "assists": row.get("assists", 0),
                    "steals": row.get("steals", 0),
                    "blocks": row.get("blocks", 0),
                    "fouls": row.get("fouls", 0),
                    "turnovers": row.get("turnovers", 0),
                    "points": row.get("points", 0),
                },
            )
            seen_ids.add(stat.id)

        if rows:
            PlayerGameStat.objects.filter(game=game).exclude(id__in=seen_ids).delete()
        return Response(GameSerializer(game).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[permissions.AllowAny])
    def add_event(self, request, pk=None):
        game = self.get_object()
        serializer = GameEventSerializer(data={**request.data, "game": game.id})
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        return Response(GameEventSerializer(event).data, status=status.HTTP_201_CREATED)
