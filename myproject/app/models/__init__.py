"""
Models package for the Core application.

This package organizes all database models by domain using subfolders:
- admin/:  Models related to administrative functions
- user/:   Models related to user management
- basketball/: Models related to basketball analytics and tournaments

Example usage:
    from core.models.user.user import User
    from core.models.admin.role import AdminRole
    from core.models.basketball import Player, Team, Bracket
"""

# Import models here to make them available at the package level
# from core.models.user.user import User
# from core.models.admin.role import AdminRole

# Basketball domain models
from .basketball import (
    Bracket,
    Game,
    GameEvent,
    GamePrediction,
    Matchup,
    Player,
    PlayerGameStat,
    Team,
    TeamStanding,
    UserProfile,
)

__all__ = [
    "Player",
    "Team",
    "Bracket",
    "Matchup",
    "TeamStanding",
    "GamePrediction",
    "Game",
    "PlayerGameStat",
    "GameEvent",
    "UserProfile",
]
