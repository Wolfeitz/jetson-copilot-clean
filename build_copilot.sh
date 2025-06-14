#!/bin/bash

echo "Building Jetson Copilot V3.1.3 (Hardened SaaS Build)..."

DOCKER_BUILDKIT=0 docker build --network=host -t jetson-copilot:clean-v3.1.3 .

echo "✅ Build complete."
