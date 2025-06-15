#!/bin/bash

echo "🚨 FULL DOCKER WIPE STARTING 🚨"
read -p "Are you absolutely sure? This will delete EVERYTHING (containers, images, volumes, networks) [y/N]: " confirm
if [[ $confirm != "y" ]]; then
  echo "❌ Cancelled."
  exit 1
fi

echo "🔧 Stopping all containers..."
docker ps -q | xargs -r docker stop

echo "🔧 Removing all containers..."
docker ps -aq | xargs -r docker rm

echo "🔧 Removing all volumes..."
docker volume rm $(docker volume ls -q)

echo "🔧 Removing all images..."
docker rmi $(docker images -q)

echo "✅ DOCKER FULL WIPE COMPLETE"
