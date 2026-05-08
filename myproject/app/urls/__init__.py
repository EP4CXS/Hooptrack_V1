from django.http import JsonResponse
from django.urls import path

from app.views.frontend import page_view


def healthcheck(_request):
    return JsonResponse({"status": "ok", "service": "hooptrack"})


urlpatterns = [
    path("health/", healthcheck, name="healthcheck"),
    path("", page_view, {"page_name": "home"}, name="home"),
    path("dashboard/", page_view, {"page_name": "dashboard"}, name="dashboard"),
    path("login/", page_view, {"page_name": "login"}, name="login"),
    path("signup/", page_view, {"page_name": "signup"}, name="signup"),
    path("analytics/", page_view, {"page_name": "analytics"}, name="analytics"),
    path("players/", page_view, {"page_name": "players"}, name="players"),
    path("players/<int:entity_id>/", page_view, {"page_name": "player-profile"}, name="player-profile"),
    path("teams/", page_view, {"page_name": "teams"}, name="teams"),
    path("teams/new/", page_view, {"page_name": "add-team"}, name="add-team"),
    path("teams/<int:entity_id>/", page_view, {"page_name": "team-roster"}, name="team-roster"),
    path("bracket/", page_view, {"page_name": "bracket"}, name="bracket"),
    path("games/", page_view, {"page_name": "games"}, name="games"),
    path("predictions/", page_view, {"page_name": "predictions"}, name="predictions"),
    path("reports/", page_view, {"page_name": "reports"}, name="reports"),
    path("settings/", page_view, {"page_name": "settings"}, name="settings"),
    path("help/", page_view, {"page_name": "help"}, name="help"),
]
