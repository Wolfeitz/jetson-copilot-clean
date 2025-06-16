# Base image (ARM64 Jetson-compatible Ubuntu)
FROM arm64v8/ubuntu:22.04

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    python3.10 python3.10-dev python3.10-distutils python3-pip \
    curl git wget libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Set default python version
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Upgrade pip + pip-tools
RUN python -m pip install --upgrade pip
RUN pip install pip-tools

# Install base requirements
COPY requirements.in .
RUN pip-compile requirements.in
RUN pip install --no-cache-dir -r requirements.txt

# Install modular llama-index packages for Ollama integration
RUN pip install llama-index-llms-ollama==0.6.2 llama-index-embeddings-ollama==0.6.0

# Copy app code into container
WORKDIR /app
COPY streamlit_app/ /app

# Expose Streamlit port
EXPOSE 8501

# Startup Streamlit server
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
