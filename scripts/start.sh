#!/bin/bash
# Start full stack (Flask + MySQL + Monitoring)
#
# Docker 29 + overlayfs workaround:
# cAdvisor expects layer metadata at a path Docker 29 no longer writes to.
# We create shim mount-id files so cAdvisor can resolve container names.
# This must run after containers exist, so we do it post-up.

set -e

echo "Starting full stack..."
docker compose -f docker-compose.yml up -d

echo "Applying cAdvisor overlayfs shim (Docker 29 compatibility)..."
for id in $(sudo ls /var/lib/docker/containers/); do
  sudo mkdir -p /var/lib/docker/image/overlayfs/layerdb/mounts/$id
  echo -n "$id" | sudo tee /var/lib/docker/image/overlayfs/layerdb/mounts/$id/mount-id > /dev/null
done
docker compose restart cadvisor > /dev/null 2>&1

echo "All services started successfully!"
