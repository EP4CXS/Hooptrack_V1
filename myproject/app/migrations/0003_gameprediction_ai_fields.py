from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0002_game_playergamestat_gameevent"),
    ]

    operations = [
        migrations.AddField(
            model_name="gameprediction",
            name="reasoning",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="gameprediction",
            name="factors",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="gameprediction",
            name="generated_by",
            field=models.CharField(
                choices=[("ai", "AI"), ("user", "User")],
                default="ai",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="gameprediction",
            name="model_name",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
    ]
