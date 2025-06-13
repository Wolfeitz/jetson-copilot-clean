#!/bin/bash

echo "Building Jetson Copilot Clean Build V2.0 Docker image..."
docker build --network=host -t jetson-copilot-clean:clean-v2 .
echo "✅ Build complete."
