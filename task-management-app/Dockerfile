FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

# Use Gunicorn for production and bind to the Render-provided $PORT (shell form expands env vars)
ENV PORT=8000
CMD python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn myproject.wsgi:application --bind 0.0.0.0:$PORT
