FROM arm64v8/ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system packages (minimal, SaaS-friendly)
RUN apt-get update && apt-get install -y \
    python3.10 python3.10-dev python3.10-distutils python3-pip \
    git curl wget libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Set default python version
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Upgrade pip
RUN python -m pip install --upgrade pip

# Use Docker layer caching correctly
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code AFTER pip install to maximize Docker caching
COPY . /app
WORKDIR /app
