# Software-Agile-Assignment
QA Module for Degree with DB

Seeded credentials and sample data

- Admin user: `admin` / `adminpass`
- Regular user: `user` / `userpass`

To create the sample data (including the seeded users) run:

```bash
python manage.py migrate
python manage.py generate_tasks

# Run locally (PowerShell)
$env:DEBUG = '1'; python manage.py runserver 0.0.0.0:8000

# Or on Linux / macOS
export DEBUG=1 && python manage.py runserver 0.0.0.0:8000
```

After running `generate_tasks` the database will contain 500 sample tasks and the two users above.

Notes
- The project reads `DEBUG` from the environment. Set `DEBUG=1` for a local/dev HTTP server without production-only security headers (HSTS, secure cookies).
- The `docker-compose.dev.yml` file starts the app with `DEBUG=1` already.
- If your browser previously accessed the site over HTTPS and cached HSTS, open an Incognito window or clear HSTS for `localhost` to avoid forced HTTPS.

Settings modules
- Local development: `myproject.settings_local` (used by `docker-compose.dev.yml` and recommended for running on your machine).
- Production/Dev: `myproject.settings_prod` (use in your deployment environment by setting `DJANGO_SETTINGS_MODULE=myproject.settings_prod`).

To run locally using the local settings explicitly:

```powershell
$env:DJANGO_SETTINGS_MODULE = 'myproject.settings_local'
$env:DEBUG = '1'
python manage.py runserver 0.0.0.0:8000
```

To run production settings locally (for testing hardened behavior):

```powershell
$env:DJANGO_SETTINGS_MODULE = 'myproject.settings_prod'
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
