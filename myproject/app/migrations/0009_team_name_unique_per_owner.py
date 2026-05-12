from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0008_owner_isolation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="team",
            name="name",
            field=models.CharField(max_length=100),
        ),
        migrations.AddConstraint(
            model_name="team",
            constraint=models.UniqueConstraint(fields=("created_by", "name"), name="uniq_team_name_per_owner"),
        ),
    ]

