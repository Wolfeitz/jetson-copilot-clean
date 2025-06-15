#!/bin/bash

echo "🚀 Building Jetson Copilot V4.3 SaaS Docker Image..."

DOCKER_BUILDKIT=0 docker build --network=host -t jetson-copilot:v4.3 .

echo "✅ Build complete."
