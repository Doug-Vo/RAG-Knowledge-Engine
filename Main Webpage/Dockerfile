# Use a lightweight Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir keeps the image smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Environment variables can be set here or at runtime
# ENV FLASK_APP=app.py

# Command to run the application using Gunicorn (Production Server)
# Bind to 0.0.0.0 to make it accessible from outside the container
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "600", "app:app"]