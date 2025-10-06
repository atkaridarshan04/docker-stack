#!/bin/bash
# Stop all services and optionally remove volumes

set -e

echo "Stopping all services..."
docker compose -f docker-compose.yml down -v

# Uncomment the following lines if you dont want to remove volumes
# docker compose -f docker-compose.yml down

# echo "Removing MySQL volume..."
# docker volume rm docker-stack_mysql-data || true

echo "Cleanup complete."
