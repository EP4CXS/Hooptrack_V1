from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Dict, List, Optional

from django.conf import settings
from django.db.models import Count, IntegerField, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from app.models.basketball.models import Player, PlayerGameStat
from app.services.groq_completion import groq_chat_completion, groq_is_configured

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser

logger = logging.getLogger(__name__)


class ChatbotService:
    """Chatbot: Groq when ``GROQ_API_KEY`` is set; otherwise rule-based fallback replies."""

    @staticmethod
    def _build_messages(
        user_message: str, history: Optional[List[dict]], user: Optional["AbstractBaseUser"] = None
    ) -> List[dict]:
        scope_note = ""
        if user is not None and getattr(user, "is_authenticated", False):
            profile = getattr(user, "profile", None)
            muni = (getattr(profile, "municipality", None) or "").strip()
            my_players = Player.objects.filter(created_by=user).count()
            scope_note = (
                f"\n6) This user is signed in. For counts and rankings, only discuss players they registered "
                f"under their account (currently {my_players} player(s))"
                + (f" in municipality scope «{muni}»." if muni else ".")
            )
        messages: List[dict] = [
            {
                "role": "system",
                "content": (
                    "You are HoopTrack Assistant for basketball league operations.\n"
                    "Rules:\n"
                    "1) Never invent players, stats, teams, or records.\n"
                    "2) If data is missing, say it clearly and suggest what to record next.\n"
                    "3) Never output placeholders like [Insert ...], TBD, or fake names.\n"
                    "4) Be concise and practical (2-6 short bullet points when helpful).\n"
                    "5) Focus on app features: teams, players, brackets, games, predictions, settings."
                    f"{scope_note}"
                ),
            }
        ]

        # Keep only the most recent turns to cap payload size.
        for item in (history or [])[-6:]:
            role = str(item.get("role") or "").strip().lower()
            content = str(item.get("content") or "").strip()
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": user_message})
        return messages

    @staticmethod
    def _stats_available() -> bool:
        return PlayerGameStat.objects.exists()

    @staticmethod
    def _is_leaderboard_query(user_message: str) -> bool:
        text = user_message.lower()
        keywords = (
            "leading player",
            "top player",
            "best player",
            "season leader",
            "top performer",
            "ppg leader",
            "nangunguna",
            "leader in",
            "who is leading",
            "who's leading",
        )
        return any(k in text for k in keywords)

    @staticmethod
    def _extract_season_year(user_message: str) -> Optional[int]:
        text = (user_message or "").lower()
        year_match = re.search(r"\b(20\d{2})\b", text)
        if year_match:
            return int(year_match.group(1))
        if any(term in text for term in ("past season", "last season", "previous season")):
            return timezone.now().year - 1
        return None

    @staticmethod
    def _season_leading_player_reply(
        user_message: str, user: Optional["AbstractBaseUser"] = None
    ) -> Optional[Dict[str, str]]:
        if not ChatbotService._is_leaderboard_query(user_message):
            return None

        season_year = ChatbotService._extract_season_year(user_message)
        base_qs = PlayerGameStat.objects.select_related("game", "player")
        if user is not None and getattr(user, "is_authenticated", False):
            base_qs = base_qs.filter(player__created_by=user)
        if season_year:
            base_qs = base_qs.filter(game__season_year=season_year)

        leader_rows = list(
            base_qs.values("player_id", "player__name")
            .annotate(total_points=Sum("points"), games_played=Count("game", distinct=True))
        )
        if not leader_rows:
            suffix = f" for season {season_year}" if season_year else ""
            return {
                "reply": (
                    f"No leading player can be identified yet{suffix} because player performance stats "
                    "are not recorded. Record game stats first, then I can rank players."
                ),
                "model": "guard-no-stats",
            }

        best = max(
            leader_rows,
            key=lambda row: (
                (row["total_points"] or 0) / max(row["games_played"] or 1, 1),
                row["total_points"] or 0,
            ),
        )
        player_id = best["player_id"]
        player_name = best["player__name"]
        total_points = int(best["total_points"] or 0)
        games_played = int(best["games_played"] or 0)
        ppg = (total_points / games_played) if games_played else 0.0

        leader_stat_qs = PlayerGameStat.objects.select_related("game").filter(player_id=player_id)
        if season_year:
            leader_stat_qs = leader_stat_qs.filter(game__season_year=season_year)
        leader_stat = leader_stat_qs.order_by("-game__updated_at", "-id").first()
        team_name = leader_stat.team_name if leader_stat and leader_stat.team_name else "Unknown Team"

        label = f"{season_year} season" if season_year else "current recorded season data"
        return {
            "reply": (
                f"Leading player for {label}: {player_name} ({team_name}) with "
                f"{ppg:.1f} PPG across {games_played} game(s), {total_points} total points."
            ),
            "model": "db-season-leader",
        }

    @staticmethod
    def _sanitize_reply(reply: str) -> str:
        text = (reply or "").strip()
        if not text:
            return ""
        # Block placeholder-style outputs that look fabricated.
        placeholder_patterns = [
            r"\[insert[^\]]*\]",
            r"\[player name\]",
            r"\[team name\]",
            r"\[points per game[^\]]*\]",
        ]
        for pattern in placeholder_patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                return (
                    "No leading player can be identified yet because player performance stats "
                    "are not recorded. Record game and player stats first, then ask again."
                )
        return text

    @staticmethod
    def _call_groq(messages: List[dict]) -> Dict[str, str]:
        model = getattr(settings, "GROQ_MODEL", "openai/gpt-oss-20b")
        timeout = int(getattr(settings, "GROQ_TIMEOUT_SECONDS", 90))
        out = groq_chat_completion(
            messages,
            model=model,
            temperature=0.35,
            timeout=timeout,
        )
        reply = ChatbotService._sanitize_reply(out["content"])
        if not reply:
            raise ValueError("Groq returned an empty response")
        return {"reply": reply, "model": out.get("model", model)}

    @staticmethod
    def _fallback_reply(user_message: str) -> Dict[str, str]:
        text = user_message.lower()
        if "team" in text:
            reply = "Open Teams to manage roster cards, then use View Roster for players."
        elif "bracket" in text:
            reply = "Go to Brackets to create format, assign teams, and track matchups."
        elif "game" in text:
            reply = "Use Games to record scores, events, and sync player box stats."
        elif "prediction" in text:
            reply = "Predictions page can generate winner picks from matchup/team trends."
        else:
            reply = "I can help with Teams, Players, Brackets, Games, Predictions, and account setup."
        return {"reply": reply, "model": "fallback-rules"}

    @staticmethod
    def ask(
        message: str, history: Optional[List[dict]] = None, user: Optional["AbstractBaseUser"] = None
    ) -> Dict[str, str]:
        # Check for player count queries first
        player_count_reply = ChatbotService._player_count_reply(message, user=user)
        if player_count_reply:
            return player_count_reply

        shooting_reply = ChatbotService._shooting_strength_reply(message, user=user)
        if shooting_reply:
            return shooting_reply

        # Check for leaderboard queries
        leaderboard_reply = ChatbotService._season_leading_player_reply(message, user=user)
        if leaderboard_reply:
            return leaderboard_reply

        messages = ChatbotService._build_messages(message, history, user=user)
        if groq_is_configured():
            try:
                return ChatbotService._call_groq(messages)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Groq chatbot call failed: %s", exc)
                return ChatbotService._fallback_reply(message)
        return ChatbotService._fallback_reply(message)
    @staticmethod
    def _is_player_count_query(user_message: str) -> bool:
        text = user_message.lower()
        keywords = (
            "how many players",
            "player count",
            "total players",
            "number of players",
            "players registered",
            "registered players",
            "players in system",
            "player total",
        )
        return any(k in text for k in keywords)
    @staticmethod
    def _player_count_reply(
        user_message: str, user: Optional["AbstractBaseUser"] = None
    ) -> Optional[Dict[str, str]]:
        if not ChatbotService._is_player_count_query(user_message):
            return None

        if user is None or not getattr(user, "is_authenticated", False):
            return {
                "reply": (
                    "Sign in to your HoopTrack account and ask again — player totals are scoped to "
                    "the players registered under your admin account (your league/municipality scope)."
                ),
                "model": "db-player-count-auth-required",
            }

        count = Player.objects.filter(created_by=user).count()
        profile = getattr(user, "profile", None)
        muni = (getattr(profile, "municipality", None) or "").strip()
        scope = f" for your municipality ({muni})" if muni else " under your account"
        return {
            "reply": (
                f"You have {count} player(s) registered{scope}. "
                "(This count includes only players you added while signed in.)"
            ),
            "model": "db-player-count",
        }

    @staticmethod
    def _is_shooting_strength_query(user_message: str) -> bool:
        text = user_message.lower()
        keys = (
            "shooting",
            "shooter",
            "fg%",
            "field goal",
            "three point",
            "3pt",
            "3-point",
            "strong in shooting",
            "best shooter",
            "good shooter",
            "who shoots",
        )
        return any(k in text for k in keys)

    @staticmethod
    def _shooting_strength_reply(
        user_message: str, user: Optional["AbstractBaseUser"] = None
    ) -> Optional[Dict[str, str]]:
        if not ChatbotService._is_shooting_strength_query(user_message):
            return None

        if user is None or not getattr(user, "is_authenticated", False):
            return {
                "reply": (
                    "Sign in to your HoopTrack account. Shooting rankings use box-score field goals "
                    "from games you record and save when they end."
                ),
                "model": "db-shooting-auth-required",
            }

        season_year = ChatbotService._extract_season_year(user_message)
        qs = PlayerGameStat.objects.filter(player__created_by=user)
        if season_year:
            qs = qs.filter(season_year=season_year)

        rows = list(
            qs.values("player_id", "player__name")
            .annotate(
                m2=Coalesce(Sum("fgm2"), Value(0), output_field=IntegerField()),
                a2=Coalesce(Sum("fga2"), Value(0), output_field=IntegerField()),
                m3=Coalesce(Sum("fgm3"), Value(0), output_field=IntegerField()),
                a3=Coalesce(Sum("fga3"), Value(0), output_field=IntegerField()),
            )
        )
        min_attempts = 5
        best: Optional[tuple] = None  # (pct, fga, fgm, name)
        for row in rows:
            fgm = int(row["m2"] or 0) + int(row["m3"] or 0)
            fga = int(row["a2"] or 0) + int(row["a3"] or 0)
            if fga < min_attempts:
                continue
            pct = fgm / fga
            name = row["player__name"] or "Player"
            cand = (pct, fga, fgm, name)
            if best is None or pct > best[0] or (pct == best[0] and fga > best[1]):
                best = cand

        season_note = f" for season {season_year}" if season_year else ""
        if not best:
            return {
                "reply": (
                    f"No field-goal sample yet{season_note} (need at least {min_attempts} FGA from your recorded games). "
                    "Use Games to log 2PT/3PT makes and misses, then save when the game ends — each game's player stats "
                    "are stored with tournament name and completion date for history."
                ),
                "model": "guard-no-fg-stats",
            }

        pct, fga, fgm, name = best
        return {
            "reply": (
                f"From your recorded box scores{season_note}, {name} has the best field-goal efficiency "
                f"among your players ({fgm}/{fga} FGs, {pct * 100:.1f}%). "
                "Rankings use per-game stats saved when you complete a game."
            ),
            "model": "db-shooting-leader",
        }

