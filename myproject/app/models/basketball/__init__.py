"""
Basketball domain models package.

Contains all models related to basketball analytics:
- Player and team management
- Tournament brackets and matchups
- Game predictions and analytics

This domain handles all basketball-related data and tournament management.
"""

# Action/functionality-partitioned model modules (compatibility exports).
from .player_model import Player
from .team_model import Team
from .bracket_model import Bracket
from .matchup_model import Matchup
from .team_standing_model import TeamStanding
from .game_prediction_model import GamePrediction
from .game_model import Game
from .player_game_stat_model import PlayerGameStat
from .game_event_model import GameEvent
from .user_profile_model import UserProfile

__all__ = [
    'Player',
    'Team',
    'Bracket',
    'Matchup',
    'TeamStanding',
    'GamePrediction',
    'Game',
    'PlayerGameStat',
    'GameEvent',
    'UserProfile',
]