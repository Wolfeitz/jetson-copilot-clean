#!/bin/bash

echo "Building Jetson Copilot V3.2 Docker image..."
DOCKER_BUILDKIT=1 docker build --network=host -t jetson-copilot:clean-v3.2 .
echo "✅ Build complete."