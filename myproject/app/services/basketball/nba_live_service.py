import json
from datetime import datetime, timezone
from urllib import request


def _format_quarter(period, state, completed):
    if completed or state == "post":
        return "Final"
    if state != "in":
        return "Scheduled"
    if not period:
        return "Live"
    if period <= 4:
        return f"Q{period}"
    if period == 5:
        return "OT"
    return f"{period - 4}OT"


def nba_live_action_service():
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    req = request.Request(url=url, method="GET", headers={"Accept": "application/json"})
    with request.urlopen(req, timeout=10) as res:
        body = res.read().decode("utf-8")
    data = json.loads(body) if body else {}

    games = []
    for event in data.get("events", []):
        competition = (event.get("competitions") or [{}])[0]
        competitors = competition.get("competitors") or []
        home = next((c for c in competitors if c.get("homeAway") == "home"), None)
        away = next((c for c in competitors if c.get("homeAway") == "away"), None)
        if not home or not away:
            continue

        status_block = competition.get("status") or {}
        status_type = status_block.get("type") or {}
        state = (status_type.get("state") or "").lower()
        completed = bool(status_type.get("completed"))
        period = int(status_block.get("period") or 0)
        display_clock = status_block.get("displayClock") or ""

        game_status = "pending"
        if completed or state == "post":
            game_status = "completed"
        elif state == "in":
            game_status = "in-progress"

        games.append(
            {
                "id": event.get("id"),
                "team1": away.get("team", {}).get("displayName") or "Away",
                "team2": home.get("team", {}).get("displayName") or "Home",
                "score1": int(away.get("score") or 0),
                "score2": int(home.get("score") or 0),
                "status": game_status,
                "quarter": _format_quarter(period=period, state=state, completed=completed),
                "clock": display_clock,
                "period": period,
                "start_time": competition.get("date") or event.get("date"),
                "summary": status_type.get("shortDetail") or status_type.get("detail") or "",
            }
        )

    return {
        "source": "espn",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "live_count": sum(1 for g in games if g["status"] == "in-progress"),
        "games": games,
    }
