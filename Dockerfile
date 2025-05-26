FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry==1.7.1

# Copy poetry files first
COPY pyproject.toml poetry.lock ./

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy project files
COPY . .

# Create static and media directories
RUN mkdir -p /app/static /app/media

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["poetry", "run", "gunicorn", "247csa.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"] 