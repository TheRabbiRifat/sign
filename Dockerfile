# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Update system and install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository universe \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7 \
    libtiff5 \
    libwebp-dev \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Expose the port Flask runs on
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
