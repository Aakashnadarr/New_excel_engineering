# Python/Django Dockerfile for standalone docker run (no docker-compose)
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies first to leverage layer cache
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /app

# Collect static files if needed
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# Default command (Gunicorn production server)
# Replace gunicorn with daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "newengineering.asgi:application"]
