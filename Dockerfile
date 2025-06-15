FROM arm64v8/ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system packages
RUN apt-get update && apt-get install -y \
    python3.10 python3.10-dev python3.10-distutils python3-pip \
    git curl wget libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Set default python version
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Upgrade pip
RUN python -m pip install --upgrade pip

# Install pip-tools for dependency resolution
RUN pip install pip-tools

# Copy requirement input file
COPY requirements.in .

# Compile full dependency lock
RUN pip-compile requirements.in

# Install fully resolved requirements
RUN pip install --no-cache-dir -r requirements.txt

# Only copy the app source code after installing dependencies
WORKDIR /app
COPY streamlit_app/ /app

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
# Entrypoint stays simple — driven from run_copilot.sh
