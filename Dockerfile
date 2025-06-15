FROM arm64v8/ubuntu:22.04

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

# Clone llama_index repo
RUN git clone https://github.com/jerryjliu/llama_index.git /llama_index
WORKDIR /llama_index

RUN pip install ./llama_index/llms/ollama
RUN pip install ./llama_index/embeddings/ollama


# Copy application code
WORKDIR /app
COPY streamlit_app/ /app

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
