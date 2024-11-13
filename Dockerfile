# Use the official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY src/ /app/src

# Expose ports (optional, mainly for documentation; Docker Compose handles actual port binding)
EXPOSE 8000 8010 8020
