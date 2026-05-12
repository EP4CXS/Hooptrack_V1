from django.db import migrations, models


def backfill_player_municipality(apps, schema_editor):
    Player = apps.get_model("app", "Player")
    UserProfile = apps.get_model("app", "UserProfile")
    for player in Player.objects.filter(created_by_id__isnull=False).iterator():
        try:
            prof = UserProfile.objects.get(user_id=player.created_by_id)
            muni = (prof.municipality or "").strip()
            if muni and not (player.municipality or "").strip():
                player.municipality = muni
                player.save(update_fields=["municipality"])
        except UserProfile.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0011_alter_game_season_year_alter_player_season_year_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="player",
            name="municipality",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.RunPython(backfill_player_municipality, migrations.RunPython.noop),
    ]
