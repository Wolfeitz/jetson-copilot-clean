# Use Ubuntu 22.04 base image for Jetson ARM64 or DGX x86_64 depending on target
FROM arm64v8/ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3.10 python3.10-dev python3.10-distutils python3-pip \
    curl git wget libmagic1 \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Set python version priority
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
RUN python -m pip install --upgrade pip

# Install Python packages
RUN pip install \
    streamlit \
    ollama \
    llama-index==0.10.20 \
    llama-index-llms-ollama \
    llama-index-embeddings-ollama \
    llama-index-readers-file \
    llama-index-readers-web \
    pydantic==1.10.12 \
    pymupdf \
    pdf2image \
    pytesseract \
    pillow \
    docx2txt


# Set workdir and copy app source
WORKDIR /app
COPY streamlit_app /app

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
