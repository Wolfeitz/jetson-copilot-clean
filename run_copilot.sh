#!/bin/bash

echo "Launching Jetson Copilot V3.1.3 Docker container..."

docker run --rm --runtime=nvidia --network=host -p 8501:8501 jetson-copilot:clean-v3.1.3 &
# For DGX change --runtime=nvidia to --gpus all

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
