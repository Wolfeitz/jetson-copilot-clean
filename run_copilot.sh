#!/bin/bash

echo "Launching Jetson Copilot V3.2 Docker container..."
docker run --rm --runtime=nvidia --network=host -p 8501:8501 -v $(pwd)/models:/models jetson-copilot:clean-v3.2 &
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
