from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_gameprediction_ai_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="player",
            name="height",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name="player",
            name="weight",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="player",
            name="address",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="player",
            name="contact_number",
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name="player",
            name="email",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]

