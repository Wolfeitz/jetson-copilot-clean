#!/bin/bash

echo "Launching Jetson Copilot Clean V1.0 Docker container..."
docker run --runtime=nvidia --network=host -p 8501:8501 jetson-copilot:clean-v1 &

# Wait a second to allow container to launch in background
sleep 2

echo ""
echo "======================================================"
echo "✅ Jetson Copilot container launched successfully."
echo ""

# Get LAN IP address (internal network address)
LAN_IP=$(hostname -I | awk '{print $1}')

# Get external IP (works only if device has external internet access)
EXTERNAL_IP=$(curl -s https://ipinfo.io/ip)

echo "🌐 Access your Copilot via:"
echo "  • Localhost:      http://localhost:8501"
echo "  • Local Network:  http://$LAN_IP:8501"
echo "  • Public IP (if routed): http://$EXTERNAL_IP:8501"
echo "======================================================"
echo ""
