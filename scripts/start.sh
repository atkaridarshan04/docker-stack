#!/bin/bash
# Start full stack (Flask + MySQL + Monitoring)

set -e

echo "Starting full stack..."
docker compose -f docker-compose.yml up -d

echo "All services started successfully!"
