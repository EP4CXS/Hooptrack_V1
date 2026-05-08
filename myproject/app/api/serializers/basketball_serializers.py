from rest_framework import serializers

from app.models.basketball.models import (
    Bracket,
    Game,
    GameEvent,
    GamePrediction,
    Matchup,
    Player,
    PlayerGameStat,
    Team,
    TeamStanding,
)


class TeamSerializer(serializers.ModelSerializer):
    playerCount = serializers.IntegerField(source="player_count", read_only=True)

    class Meta:
        model = Team
        fields = ["id", "name", "city", "conference", "division", "logo", "playerCount"]


class PlayerSerializer(serializers.ModelSerializer):
    team = serializers.CharField(source="team.name", allow_null=True, required=False)
    contactNumber = serializers.CharField(source="contact_number", allow_null=True, required=False, allow_blank=True)

    class Meta:
        model = Player
        fields = [
            "id",
            "name",
            "height",
            "weight",
            "position",
            "jerseyNumber",
            "team",
            "age",
            "address",
            "contactNumber",
            "email",
        ]

    jerseyNumber = serializers.CharField(source="jersey_number")


class MatchupSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="matchup_id")
    matchNumber = serializers.IntegerField(source="match_number")
    nextMatchId = serializers.CharField(source="next_matchup_id", allow_null=True, required=False)
    loserNextMatchId = serializers.CharField(source="loser_next_matchup_id", allow_null=True, required=False)
    scheduledDate = serializers.DateField(source="scheduled_date", allow_null=True, required=False)
    scheduledTime = serializers.TimeField(source="scheduled_time", allow_null=True, required=False)
    isBye = serializers.BooleanField(source="is_bye", required=False)
    isBronzeMatch = serializers.BooleanField(source="is_bronze_match", required=False)
    bracketType = serializers.CharField(source="bracket_type", allow_null=True, required=False)
    bracketGroup = serializers.IntegerField(source="bracket_group", allow_null=True, required=False)

    class Meta:
        model = Matchup
        fields = [
            "id",
            "team1",
            "team2",
            "winner",
            "score1",
            "score2",
            "round",
            "matchNumber",
            "nextMatchId",
            "loserNextMatchId",
            "status",
            "scheduledDate",
            "scheduledTime",
            "venue",
            "isBye",
            "isBronzeMatch",
            "bracketType",
            "bracketGroup",
            "stage",
        ]


class TeamStandingSerializer(serializers.ModelSerializer):
    bracketGroup = serializers.IntegerField(source="bracket_group", allow_null=True, required=False)
    matchesPlayed = serializers.IntegerField(source="matches_played")

    class Meta:
        model = TeamStanding
        fields = ["team", "wins", "losses", "points", "matchesPlayed", "bracketGroup"]


class BracketSerializer(serializers.ModelSerializer):
    matchups = MatchupSerializer(source="matchup_set", many=True, read_only=True)
    standings = TeamStandingSerializer(source="teamstanding_set", many=True, read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    currentRound = serializers.IntegerField(source="current_round")
    totalRounds = serializers.IntegerField(source="total_rounds")
    startDate = serializers.DateField(source="start_date", allow_null=True, required=False)
    includeBronzeMatch = serializers.BooleanField(source="include_bronze_match", required=False)
    includeQuarterFinals = serializers.BooleanField(source="include_quarter_finals", required=False)
    roundRobinConfig = serializers.JSONField(source="round_robin_config", required=False)
    finalRankings = serializers.JSONField(source="final_rankings", required=False)

    class Meta:
        model = Bracket
        fields = [
            "id",
            "name",
            "format",
            "teams",
            "matchups",
            "currentRound",
            "totalRounds",
            "createdAt",
            "status",
            "startDate",
            "location",
            "includeBronzeMatch",
            "includeQuarterFinals",
            "standings",
            "finalRankings",
            "roundRobinConfig",
        ]


class GamePredictionSerializer(serializers.ModelSerializer):
    matchupId = serializers.CharField(source="matchup.matchup_id")
    bracketId = serializers.IntegerField(source="matchup.bracket_id", read_only=True)
    bracketName = serializers.CharField(source="matchup.bracket.name", read_only=True)
    predictedWinner = serializers.CharField(source="predicted_winner")
    generatedBy = serializers.CharField(source="generated_by", required=False)
    modelName = serializers.CharField(source="model_name", required=False, allow_blank=True)

    class Meta:
        model = GamePrediction
        fields = [
            "id",
            "matchupId",
            "bracketId",
            "bracketName",
            "predictedWinner",
            "confidence",
            "reasoning",
            "factors",
            "generatedBy",
            "modelName",
            "created_at",
        ]


class PlayerGameStatSerializer(serializers.ModelSerializer):
    playerName = serializers.CharField(source="player.name", read_only=True)
    jerseyNumber = serializers.CharField(source="player.jersey_number", read_only=True)
    teamName = serializers.CharField(source="team_name")

    class Meta:
        model = PlayerGameStat
        fields = [
            "id",
            "player",
            "playerName",
            "jerseyNumber",
            "teamName",
            "fgm2",
            "fga2",
            "fgm3",
            "fga3",
            "ftm",
            "fta",
            "oreb",
            "dreb",
            "assists",
            "steals",
            "blocks",
            "fouls",
            "turnovers",
            "points",
        ]


class GameEventSerializer(serializers.ModelSerializer):
    playerName = serializers.CharField(source="player.name", read_only=True)
    teamName = serializers.CharField(source="team_name")
    gameTime = serializers.CharField(source="game_time")
    eventType = serializers.CharField(source="event_type")

    class Meta:
        model = GameEvent
        fields = [
            "id",
            "game",
            "player",
            "playerName",
            "teamName",
            "eventType",
            "quarter",
            "gameTime",
            "description",
            "created_at",
        ]


class GameSerializer(serializers.ModelSerializer):
    team1Name = serializers.CharField(source="team1_name")
    team2Name = serializers.CharField(source="team2_name")
    playerStats = PlayerGameStatSerializer(source="player_stats", many=True, read_only=True)
    events = GameEventSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = [
            "id",
            "bracket",
            "matchup",
            "team1Name",
            "team2Name",
            "score1",
            "score2",
            "quarter",
            "clock",
            "status",
            "playerStats",
            "events",
            "created_at",
            "updated_at",
        ]
