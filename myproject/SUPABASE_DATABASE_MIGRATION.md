# Supabase Database Migration (Incremental, DB-Only)

This guide migrates this Django project to a Supabase-hosted PostgreSQL database while keeping the existing Django API, views, and auth flow.

## 1) Collect Supabase Credentials

From Supabase dashboard (`Project Settings` -> `Database`), collect:

- Host (`db.<project-ref>.supabase.co` or pooler host)
- Port
- Database name (usually `postgres`)
- User
- Password

For production app traffic, use the Supabase transaction pooler endpoint.

## 2) Configure Environment

Copy `.env.example` to `.env`, then set database variables:

```env
USE_SQLITE_LOCAL=False
DB_NAME=postgres
DB_USER=<supabase-user>
DB_PASSWORD=<supabase-password>
DB_HOST=<supabase-host-or-pooler-host>
DB_PORT=5432
DB_SSLMODE=require
DB_CONN_MAX_AGE=300
DB_CONNECT_TIMEOUT=10
```

Notes:
- `USE_SQLITE_LOCAL=False` makes local settings use PostgreSQL config.
- `DB_SSLMODE=require` is recommended for Supabase.

## 3) Run Migrations Against Supabase

Run from the `myproject` directory:

```bash
python manage.py migrate
python manage.py showmigrations
python manage.py verify_supabase_setup
```

`verify_supabase_setup` checks critical tables and row counts.

## 4) Migrate Existing Data (from old DB)

### A. Export data from old database

Use your existing DB environment values first, then run:

```bash
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.permission -e sessions.session -e admin.logentry > data_migration.json
```

### B. Import into Supabase

Switch environment to Supabase DB values, then run:

```bash
python manage.py loaddata data_migration.json
python manage.py verify_supabase_setup
```

## 5) Validate End-to-End Behavior

Run server and test core flows:

```bash
python manage.py runserver
```

Manual verification checklist:
- Login and token issuance still works.
- Teams CRUD works.
- Players CRUD works.
- Brackets create/update/delete works.
- Games and predictions pages load and save data.

## 6) Production Hardening Checklist

- Keep `DEBUG=False` in production.
- Set strict `ALLOWED_HOSTS`.
- Store DB credentials in secret manager or protected env vars.
- Rotate DB password after migration.
- Restrict DB access to required environments/services only.
- Validate Supabase backups and periodic restore drills.
