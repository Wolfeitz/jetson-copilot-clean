#!/bin/bash

echo "Building Jetson Copilot Clean V1.0 Docker image..."
docker build --network=host -t jetson-copilot:clean-v1 .

echo "✅ Build complete."
