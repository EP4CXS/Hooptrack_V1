from django.db import migrations, models


def backfill_game_and_stat_context(apps, schema_editor):
    Game = apps.get_model("app", "Game")
    Bracket = apps.get_model("app", "Bracket")
    PlayerGameStat = apps.get_model("app", "PlayerGameStat")

    for game in Game.objects.select_related().iterator():
        updated = []
        if game.bracket_id:
            try:
                b = Bracket.objects.get(pk=game.bracket_id)
                if b.name and not (game.tournament_name or "").strip():
                    game.tournament_name = b.name
                    updated.append("tournament_name")
            except Bracket.DoesNotExist:
                pass
        if game.status == "completed" and game.completed_at is None:
            game.completed_at = game.updated_at
            updated.append("completed_at")
        if updated:
            game.save(update_fields=updated)

    for stat in PlayerGameStat.objects.select_related("game").iterator():
        g = stat.game
        stat.tournament_name = (g.tournament_name or "").strip()
        stat.game_completed_at = g.completed_at
        stat.season_year = g.season_year
        stat.save(update_fields=["tournament_name", "game_completed_at", "season_year"])


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0012_player_municipality_scope"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="tournament_name",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AddField(
            model_name="game",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="playergamestat",
            name="tournament_name",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AddField(
            model_name="playergamestat",
            name="game_completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="playergamestat",
            name="season_year",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.RunPython(backfill_game_and_stat_context, migrations.RunPython.noop),
    ]
