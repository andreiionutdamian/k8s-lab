#!/bin/sh
echo "Starting Docker daemon..."
sudo dockerd > /var/log/dockerd.log 2>&1
