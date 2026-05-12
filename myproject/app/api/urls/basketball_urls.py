from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.api.views.nba_live_view import NbaLiveActionView
from app.api.views.basketball_views import BracketViewSet, GamePredictionViewSet, GameViewSet, MatchupViewSet, PlayerViewSet, TeamViewSet

router = DefaultRouter()
router.register("players", PlayerViewSet, basename="players")
router.register("teams", TeamViewSet, basename="teams")
router.register("brackets", BracketViewSet, basename="brackets")
router.register("matchups", MatchupViewSet, basename="matchups")
router.register("predictions", GamePredictionViewSet, basename="predictions")
router.register("games", GameViewSet, basename="games")

urlpatterns = [
    path("", include(router.urls)),
    path("nba/live/", NbaLiveActionView.as_view(), name="api-nba-live"),
]
