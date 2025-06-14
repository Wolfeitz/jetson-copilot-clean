FROM arm64v8/ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    python3.10 python3.10-dev python3.10-distutils python3-pip \
    curl git wget libmagic1 \
    poppler-utils tesseract-ocr libtesseract-dev libleptonica-dev \
    && rm -rf /var/lib/apt/lists/*

# Set default python version
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Upgrade pip
RUN python -m pip install --upgrade pip

# ⚠⚠ KEY CHANGE: copy only requirements first ⚠⚠
COPY requirements.txt .

# Install Python dependencies with cache
RUN pip install --no-cache-dir -r requirements.txt

# Only after pip layer is fully cached do we copy the rest
COPY . /app
WORKDIR /app
