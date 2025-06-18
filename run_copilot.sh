#!/bin/bash

echo "🚀 Running Jetson Copilot SaaS Container..."

# ----- CONFIGURATION -----
# Path to model catalog on the host (Ollama's system directory)
MODEL_CATALOG_HOST="/usr/share/ollama/model_catalog.json"
MODEL_CATALOG_CONTAINER="/app/model_catalog.json"
CONTAINER_IMAGE="jetson-copilot:v4.3"

# Set OLLAMA_BASE_URL for host Ollama server
OLLAMA_BASE_URL="http://localhost:11434"

# ----- DOCKER RUN COMMAND -----
docker run --rm \
  --runtime=nvidia \
  --network=host \
  -e OLLAMA_BASE_URL=$OLLAMA_BASE_URL \
  -e OLLAMA_HOST=$OLLAMA_BASE_URL \
  -v "$MODEL_CATALOG_HOST":"$MODEL_CATALOG_CONTAINER":ro \
  -p 8501:8501 \
  $CONTAINER_IMAGE &

# For DGX: change --runtime=nvidia to --gpus all
#          (or remove both for CPU-only debugging)
# Remove --rm if you want the container to persist after exit

sleep 2

# Grab Jetson IP addresses for user convenience
LAN_IP=$(hostname -I | awk '{print $1}')
EXTERNAL_IP=$(curl -s https://ipinfo.io/ip)

echo ""
echo "======================================================"
echo "✅ Jetson Copilot container launched successfully."
echo ""
echo "🌐 Access your Copilot via:"
echo "  • Localhost:      http://localhost:8501"
echo "  • Local Network:  http://$LAN_IP:8501"
echo "  • Public IP (if routed): http://$EXTERNAL_IP:8501"
echo "======================================================"
echo ""
