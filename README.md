# Task Management App

A Django-based web application for managing tasks collaboratively.

---

##  Features

- User registration and authentication
- Task creation, assignment, and status tracking
- Responsive design 
- Powered by SQLite with Django ORM

---

## 🛠Requirements

- Python 3.10+
- Git
- Virtualenv (Optional)
- SQLite
- Django

---

## Local Development Setup

### 1. **Clone the Repository**

git clone https://github.com/Brandon-Niles/Software-Agile-Assignment.git

### 1. **Install Dependencies**

pip install django
### 3. **Apply Migrations**

python manage.py migrate
### 1. **Run the development server**

python manage.py runserver

## Dev & CI

- Run locally using Docker Compose: `docker-compose -f task-management-app/docker-compose.dev.yml up --build`
- CI pipelines are configured in `.github/workflows/`:
	- `feature-pipeline.yml` — runs on pushes to `feature/**` branches: lint, tests, build and push Docker image to GHCR.
	- `main-pipeline.yml` — runs on pushes to `main`: lint, tests, build and push Docker image to GHCR and marks a deployment to the `dev` environment.

To preview a built feature image locally:

```bash
# after a workflow pushes an image, pull it and run:
docker pull ghcr.io/<owner>/<repo>/task-app:feature-<branch>-<sha>
docker run --rm -p 8000:8000 ghcr.io/<owner>/<repo>/task-app:feature-<branch>-<sha>
```
