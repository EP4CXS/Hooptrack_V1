from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


def get_current_year():
    return timezone.now().year


class Player(models.Model):
    """Model for basketball players"""
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="players")
    municipality = models.CharField(max_length=100, blank=True, default="")
    name = models.CharField(max_length=100)
    season_year = models.IntegerField(default=get_current_year)
    height = models.CharField(max_length=10, null=True, blank=True)  # e.g., "206" cm
    weight = models.CharField(max_length=10, null=True, blank=True)  # e.g., "113" kg
    position = models.CharField(max_length=10)  # e.g., "SF", "PG", "C"
    jersey_number = models.CharField(max_length=10)  # e.g., "23"
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True)
    age = models.CharField(max_length=10, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.jersey_number})"


class UserProfile(models.Model):
    """Profile fields captured during signup for account settings."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    municipality = models.CharField(max_length=100, blank=True, default="")
    barangay = models.CharField(max_length=100, blank=True, default="")
    organization = models.CharField(max_length=200, blank=True, default="")
    role = models.CharField(max_length=50, default="Administrator")

    def __str__(self):
        return f"{self.user.username} profile"


class Team(models.Model):
    """Model for basketball teams"""
    CONFERENCE_CHOICES = [
        ('Eastern', 'Eastern'),
        ('Western', 'Western'),
    ]

    DIVISION_CHOICES = [
        ('midget', 'Midget'),
        ('senior', 'Senior'),
        ('junior', 'Junior'),
        ('U13', 'U13'),
        ('U14', 'U14'),
        ('U15', 'U15'),
        ('U16', 'U16'),
        ('U17', 'U17'),
        ('U18', 'U18'),
        ('U19', 'U19'),
        ('U20', 'U20'),
        ('U21', 'U21'),
    ]

    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="teams")
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    conference = models.CharField(max_length=20, choices=CONFERENCE_CHOICES)
    division = models.CharField(max_length=20, choices=DIVISION_CHOICES)
    logo = models.ImageField(upload_to="team_logos", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['created_by', 'name'], name='uniq_team_name_per_owner'),
        ]

    def __str__(self):
        return f"{self.city} {self.name}"

    @property
    def player_count(self):
        return self.player_set.count()


class Bracket(models.Model):
    """Model for tournament brackets"""
    FORMAT_CHOICES = [
        ('single-elimination', 'Single Elimination'),
        ('double-elimination', 'Double Elimination'),
        ('round-robin', 'Round Robin'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="brackets")
    name = models.CharField(max_length=200)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES)
    teams = models.JSONField()  # List of team names
    current_round = models.IntegerField(default=1)
    total_rounds = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    # Bracket-specific options
    include_bronze_match = models.BooleanField(default=False)
    include_quarter_finals = models.BooleanField(default=False)
    round_robin_config = models.JSONField(null=True, blank=True)  # Configuration for round-robin

    # Results
    final_rankings = models.JSONField(null=True, blank=True)  # {'first': team_name, 'second': team_name, etc.}

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.format})"


class Matchup(models.Model):
    """Model for individual matchups in brackets"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    STAGE_CHOICES = [
        ('group', 'Group Stage'),
        ('crossover', 'Crossover'),
        ('semifinal', 'Semifinal'),
        ('final', 'Final'),
        ('bronze', 'Bronze Match'),
    ]

    BRACKET_TYPE_CHOICES = [
        ('winners', 'Winners Bracket'),
        ('losers', 'Losers Bracket'),
        ('grand-final', 'Grand Final'),
        ('if-game', 'If Game'),
        ('crossover', 'Crossover'),
        ('playoff', 'Playoff'),
    ]

    bracket = models.ForeignKey(Bracket, on_delete=models.CASCADE)
    matchup_id = models.CharField(max_length=50)  # e.g., 'r1m1', 'w-r1-m1'
    team1 = models.CharField(max_length=100, null=True, blank=True)
    team2 = models.CharField(max_length=100, null=True, blank=True)
    winner = models.CharField(max_length=100, null=True, blank=True)
    score1 = models.IntegerField(null=True, blank=True)
    score2 = models.IntegerField(null=True, blank=True)
    round = models.IntegerField()
    match_number = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='group')
    bracket_type = models.CharField(max_length=20, choices=BRACKET_TYPE_CHOICES, null=True, blank=True)
    bracket_group = models.IntegerField(null=True, blank=True)  # For round-robin groups

    # Scheduling
    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.TimeField(null=True, blank=True)
    venue = models.CharField(max_length=200, null=True, blank=True)

    # Special flags
    is_bye = models.BooleanField(default=False)
    is_bronze_match = models.BooleanField(default=False)

    # Progression
    next_matchup_id = models.CharField(max_length=50, null=True, blank=True)
    loser_next_matchup_id = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ['bracket', 'round', 'match_number']
        unique_together = ['bracket', 'matchup_id']

    def __str__(self):
        return f"{self.bracket.name} - {self.matchup_id}: {self.team1 or 'TBD'} vs {self.team2 or 'TBD'}"


class TeamStanding(models.Model):
    """Model for team standings in round-robin brackets"""
    bracket = models.ForeignKey(Bracket, on_delete=models.CASCADE)
    team = models.CharField(max_length=100)
    bracket_group = models.IntegerField(null=True, blank=True)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    points = models.IntegerField(default=0)  # For round-robin scoring
    matches_played = models.IntegerField(default=0)

    class Meta:
        unique_together = ['bracket', 'team']

    def __str__(self):
        return f"{self.team} - {self.wins}W-{self.losses}L"


class GamePrediction(models.Model):
    """Model for game predictions"""
    GENERATED_BY_CHOICES = [
        ('ai', 'AI'),
        ('user', 'User'),
    ]

    matchup = models.ForeignKey(Matchup, on_delete=models.CASCADE)
    predicted_winner = models.CharField(max_length=100)
    confidence = models.IntegerField()  # Percentage 0-100
    reasoning = models.TextField(blank=True, default='')
    factors = models.JSONField(null=True, blank=True)
    generated_by = models.CharField(max_length=10, choices=GENERATED_BY_CHOICES, default='ai')
    model_name = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prediction: {self.matchup.matchup_id} - {self.predicted_winner} ({self.confidence}%)"


class Game(models.Model):
    """Live/recorded game for a bracket matchup."""
    STATUS_CHOICES = [
        ("in-progress", "In Progress"),
        ("completed", "Completed"),
    ]

    bracket = models.ForeignKey(Bracket, on_delete=models.SET_NULL, null=True, blank=True)
    matchup = models.ForeignKey(Matchup, on_delete=models.SET_NULL, null=True, blank=True)
    team1_name = models.CharField(max_length=100)
    team2_name = models.CharField(max_length=100)
    score1 = models.IntegerField(default=0)
    score2 = models.IntegerField(default=0)
    quarter = models.IntegerField(default=1)
    clock = models.CharField(max_length=16, default="12:00")
    season_year = models.IntegerField(default=get_current_year)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="in-progress")
    # Bracket/tournament label copied for history & analytics (typically Bracket.name).
    tournament_name = models.CharField(max_length=200, blank=True, default="")
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    @property
    def quarter_display(self):
        if self.quarter <= 4:
            return f"Q{self.quarter}"
        elif self.quarter == 5:
            return "OT"
        else:
            return f"{self.quarter - 4}OT"

    def __str__(self):
        return f"{self.team1_name} vs {self.team2_name} ({self.status})"


class PlayerGameStat(models.Model):
    """Per-player box score snapshot for a game."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="player_stats")
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=100)
    tournament_name = models.CharField(max_length=200, blank=True, default="")
    game_completed_at = models.DateTimeField(null=True, blank=True)
    season_year = models.IntegerField(null=True, blank=True)

    fgm2 = models.IntegerField(default=0)
    fga2 = models.IntegerField(default=0)
    fgm3 = models.IntegerField(default=0)
    fga3 = models.IntegerField(default=0)
    ftm = models.IntegerField(default=0)
    fta = models.IntegerField(default=0)
    oreb = models.IntegerField(default=0)
    dreb = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    steals = models.IntegerField(default=0)
    blocks = models.IntegerField(default=0)
    fouls = models.IntegerField(default=0)
    turnovers = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    class Meta:
        unique_together = ["game", "player"]
        ordering = ["team_name", "player__name"]

    def __str__(self):
        return f"{self.player.name} ({self.team_name}) - {self.points} pts"


class GameEvent(models.Model):
    """Timeline events for game tracking."""
    EVENT_CHOICES = [
        ("made2", "Made 2"),
        ("missed2", "Missed 2"),
        ("made3", "Made 3"),
        ("missed3", "Missed 3"),
        ("madeFT", "Made FT"),
        ("missedFT", "Missed FT"),
        ("oreb", "Offensive Rebound"),
        ("dreb", "Defensive Rebound"),
        ("assist", "Assist"),
        ("steal", "Steal"),
        ("block", "Block"),
        ("foul", "Foul"),
        ("turnover", "Turnover"),
    ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="events")
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)
    team_name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    quarter = models.IntegerField(default=1)
    game_time = models.CharField(max_length=16, default="12:00")
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.team_name} {self.event_type} Q{self.quarter} {self.game_time}"
