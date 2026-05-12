from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0005_userprofile"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="season_year",
            field=models.IntegerField(default=2026),
        ),
    ]
