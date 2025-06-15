#!/bin/bash

echo "🔧 Stopping all running containers..."
docker ps -q | xargs -r docker stop

echo "🔧 Removing all stopped containers..."
docker ps -aq | xargs -r docker rm

echo "🔧 Pruning unused volumes..."
docker volume prune -f

echo "🔧 Pruning unused images..."
docker image prune -f

echo "✅ Docker reset complete!"
