from django.db import migrations, models
import django.utils.timezone


def current_year():
    return django.utils.timezone.now().year


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0006_game_season_year"),
    ]

    operations = [
        migrations.AddField(
            model_name="player",
            name="season_year",
            field=models.IntegerField(default=current_year),
        ),
    ]

