#!/bin/sh
# Start the Docker daemon in the background
sudo dockerd &

# Execute the CMD from the Dockerfile or the command passed to docker run
exec "$@"
