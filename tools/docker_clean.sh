#!/bin/bash

echo "🔧 Pruning stopped containers..."
docker container prune -f

echo "🔧 Pruning unused volumes..."
docker volume prune -f

echo "🔧 Pruning dangling images..."
docker image prune -f

echo "🔧 Pruning unused networks..."
docker network prune -f

echo "✅ Docker clean complete!"
