# Software-Agile-Assignment
QA Module for Degree with DB

Seeded credentials and sample data

- Admin user: `admin` / `adminpass`
- Regular user: `user` / `userpass`

To create the sample data (including the seeded users) run:

```bash
python manage.py migrate
python manage.py generate_tasks
python manage.py runserver
```

After running `generate_tasks` the database will contain 500 sample tasks and the two users above.
