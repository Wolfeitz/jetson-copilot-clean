#!/bin/bash

echo "Launching Jetson Copilot Clean Build V2.0 Docker container..."
docker run --runtime=nvidia --network=host -p 8501:8501 jetson-copilot-clean:clean-v2 &
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
