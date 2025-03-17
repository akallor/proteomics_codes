#!/bin/bash
# Script to convert Skyline Docker container to Singularity

# Ensure the Docker image exists
if ! docker image inspect skyline:latest >/dev/null 2>&1; then
  echo "Error: Docker image skyline:latest not found!"
  echo "Please run the Docker creation script first."
  exit 1
fi

# 1. Save the Docker image to a tar file
echo "Saving Docker image to tar file..."
docker save skyline:latest -o skyline_docker.tar

# 2. Convert the Docker tar to a Singularity SIF file
echo "Converting Docker image to Singularity format..."
singularity build skyline.sif docker-archive://skyline_docker.tar

# 3. Clean up the tar file
rm skyline_docker.tar

echo "Singularity container created: skyline.sif"
echo "You can run it with: singularity run skyline.sif [commands]"
echo "Or: singularity exec skyline.sif skylinecmd [commands]"
