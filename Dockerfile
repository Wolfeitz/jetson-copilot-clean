# Base Jetson compatible Ubuntu 22.04 image (public, no NVIDIA login needed)
FROM arm64v8/ubuntu:22.04

# Set environment to non-interactive to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3.10 python3.10-dev python3.10-distutils python3-pip \
    curl git wget libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip safely for Python 3.10
RUN python3.10 -m pip install --upgrade pip

# Use Python 3.10 explicitly
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Install Jetson-specific CUDA packages (public Jetson meta-packages)
RUN apt-get update && apt-get install -y \
    nvidia-cuda-toolkit \
    && rm -rf /var/lib/apt/lists/*

# Install LlamaIndex full stack, streamlit and ollama client
RUN pip install \
    streamlit \
    ollama \
    llama-index==0.10.20 \
    llama-index-llms-ollama \
    llama-index-embeddings-ollama \
    llama-index-readers-file \
    llama-index-readers-web \
    pydantic==1.10.12

# Copy your Streamlit app files
COPY streamlit_app /app
WORKDIR /app

# Expose Streamlit default port
EXPOSE 8501

# Launch Streamlit automatically
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
