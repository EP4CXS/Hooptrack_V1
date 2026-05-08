from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Verify schema/data readiness when using a Supabase PostgreSQL database."

    def handle(self, *args, **options):
        db_settings = connection.settings_dict
        engine = str(db_settings.get("ENGINE", ""))
        host = str(db_settings.get("HOST", ""))
        name = str(db_settings.get("NAME", ""))
        user = str(db_settings.get("USER", ""))

        self.stdout.write(self.style.NOTICE("Database connection summary"))
        self.stdout.write(f"- ENGINE: {engine}")
        self.stdout.write(f"- HOST: {host or '(empty)'}")
        self.stdout.write(f"- NAME: {name or '(empty)'}")
        self.stdout.write(f"- USER: {user or '(empty)'}")

        if "postgresql" not in engine:
            self.stdout.write(
                self.style.WARNING(
                    "Current DB engine is not PostgreSQL. Set USE_SQLITE_LOCAL=False and DB_* vars for Supabase checks."
                )
            )

        with connection.cursor() as cursor:
            db_vendor = connection.vendor
            if db_vendor == "postgresql":
                cursor.execute(
                    "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto');"
                )
                has_pgcrypto = bool(cursor.fetchone()[0])
                if not has_pgcrypto:
                    self.stdout.write(
                        self.style.WARNING(
                            "pgcrypto extension is not enabled. Enable it if your future schema needs gen_random_uuid()."
                        )
                    )

            introspection = connection.introspection
            existing_tables = set(introspection.table_names(cursor))

        model_labels = [
            "app.Team",
            "app.Player",
            "app.Bracket",
            "app.Matchup",
            "app.TeamStanding",
            "app.Game",
            "app.GamePrediction",
            "app.PlayerGameStat",
            "app.GameEvent",
        ]
        missing_tables = []
        model_counts = []

        for label in model_labels:
            model = apps.get_model(label)
            table_name = model._meta.db_table
            if table_name not in existing_tables:
                missing_tables.append(table_name)
                continue
            model_counts.append((label, model.objects.count()))

        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("Core table status"))
        if missing_tables:
            for table_name in missing_tables:
                self.stdout.write(self.style.ERROR(f"- missing: {table_name}"))
        else:
            self.stdout.write(self.style.SUCCESS("- all required app tables exist"))

        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("Row counts"))
        for label, count in model_counts:
            self.stdout.write(f"- {label}: {count}")

        if missing_tables:
            raise SystemExit(1)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Supabase database verification passed."))
