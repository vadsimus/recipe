# Use a lightweight Python base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        pkg-config \
        default-libmysqlclient-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN python -m venv /app/.venv \
    && /app/.venv/bin/pip install --upgrade pip setuptools wheel \
    && /app/.venv/bin/pip install -r requirements.txt

# Copy application files
COPY . .

# Expose the application port
EXPOSE 8000

# Run the Django server using Uvicorn
CMD [".venv/bin/uvicorn", "recipe.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
