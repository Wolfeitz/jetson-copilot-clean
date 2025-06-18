#!/bin/bash

echo "🚀 Running Jetson Copilot V4.3 SaaS Container..."

docker run --rm --runtime=nvidia --network=host \
  -e OLLAMA_BASE_URL=http://localhost:11434 \
  -e OLLAMA_HOST=http://localhost:11434 \
  -p 8501:8501 jetson-copilot:v4.3 &

# For DGX change --runtime=nvidia to --gpus all
# remove --rm if you need feedback on startup
# Wait a second to allow container to spin up
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
