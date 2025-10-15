#!/bin/bash

# ---------------------------------------
# Docker Helper for ODMS API.
# Author: Najmul Islam <najmulislamru@gmail.com>
# Usage:
#   ./docker_run.sh
#   ./docker_run.sh run
#   ./docker_run.sh build
#   ./docker_run.sh up
#   ./docker_run.sh down
#   ./docker_run.sh migrate
#   ./docker_run.sh bash
# ---------------------------------------

set -e

case "$1" in
  run)
    echo "🔹 Starting Docker build and run process..."
    # Step 1: Stop any running containers (optional)
    echo "🛑 Stopping existing containers..."
    docker-compose down
    # Step 2: Build the image
    echo "🔧 Building Docker image..."
    docker-compose build --no-cache
    # Step 3: Run the containers
    echo "🚀 Starting containers..."
    docker-compose up
    ;;
  build)
    echo "🔧 Building Docker images..."
    docker-compose build --no-cache
    ;;
  up)
    echo "🚀 Starting containers..."
    docker-compose up
    ;;
  down)
    echo "🛑 Stopping containers..."
    docker-compose down
    ;;
  migrate)
    echo "📦 Running migrations..."
    docker-compose exec web python manage.py migrate
    ;;
  bash)
    echo "💻 Opening shell inside web container..."
    docker-compose exec web bash
    ;;
  *)
    echo "Usage: ./docker_run.sh {build|up|down|migrate|bash}"
    exit 1
    ;;
esac
