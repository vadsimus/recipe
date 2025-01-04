# Use the official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=recipe.settings \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Create a working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt /app/

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && python -m venv .venv \
    && .venv/bin/pip install --upgrade pip setuptools wheel \
    && .venv/bin/pip install -r requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY . /app/

# Run migrations and collectstatic at build time
RUN python manage.py collectstatic --noinput && python manage.py migrate

# Expose the application port
EXPOSE 8000

# Start Django with Gunicorn
CMD ["uvicorn", "recipe.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
