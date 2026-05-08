from django.shortcuts import render


def page_view(request, page_name="dashboard", entity_id=None):
    title_map = {
        "home": "Hoop Track Basketball Dashboard",
        "login": "Log In",
        "signup": "Create Account",
        "dashboard": "Dashboard",
        "analytics": "Analytics",
        "players": "Players",
        "player-profile": "Player Profile",
        "teams": "Teams",
        "add-team": "Add Team",
        "team-roster": "Team Roster",
        "bracket": "Bracket Generator",
        "games": "Game Tracking",
        "predictions": "Predictions",
        "reports": "Reports",
        "settings": "Settings",
        "help": "Help",
    }
    return render(
        request,
        "app/index.html",
        {
            "page_name": page_name,
            "page_title": title_map.get(page_name, "HoopTrack"),
            "entity_id": entity_id,
        },
    )

