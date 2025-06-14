#!/bin/bash

echo "Building Jetson Copilot V3.1.2 (Optimized Build System)..."
DOCKER_BUILDKIT=0 docker build --network=host -t jetson-copilot:clean-v3.1.2 .
echo "✅ Build complete."
