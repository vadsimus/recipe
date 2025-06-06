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
        netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# Create the logs directory
RUN mkdir -p /logs \
    && chmod 755 /logs

# Set up a volume for the logs directory
VOLUME /logs

# Copy application files
COPY . .

# Expose the application port
EXPOSE 8095

# Run the Django server using Uvicorn
CMD ["uvicorn", "recipe.asgi:application", "--host", "0.0.0.0", "--port", "8095"]
