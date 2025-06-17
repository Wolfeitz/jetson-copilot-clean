FROM arm64v8/ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    python3.10 python3.10-dev python3.10-distutils python3-pip \
    curl git wget libmagic1 \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

RUN python -m pip install --upgrade pip
RUN pip install pip-tools

COPY requirements.in .
RUN pip-compile requirements.in
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY streamlit_app/ /app

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
