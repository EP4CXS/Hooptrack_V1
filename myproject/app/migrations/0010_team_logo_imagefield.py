from django.db import migrations, models


def clear_external_team_logo_urls(apps, schema_editor):
    Team = apps.get_model("app", "Team")
    Team.objects.filter(logo__startswith="http").update(logo=None)


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0009_team_name_unique_per_owner"),
    ]

    operations = [
        migrations.RunPython(clear_external_team_logo_urls, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="team",
            name="logo",
            field=models.ImageField(blank=True, null=True, upload_to="team_logos"),
        ),
    ]
