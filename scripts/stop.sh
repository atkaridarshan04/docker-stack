#!/bin/bash
# Stop all services (data volumes are preserved)
# To also delete all data: docker compose down -v

set -e

echo "Stopping all services..."
docker compose -f docker-compose.yml down

echo "Done. Data volumes preserved."
