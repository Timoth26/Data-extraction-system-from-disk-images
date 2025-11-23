#!/bin/bash

IMAGE_PATH="$1"
shift

if [ -z "$IMAGE_PATH" ]; then
    echo "Usage: ./run_analysis.sh <path_to_disk_image> [additional_args...]"
    exit 1
fi

mkdir -p ./disk_images ./results ./temp

if [ ! -f "$IMAGE_PATH" ]; then
    echo "Error: Image file $IMAGE_PATH not found"
    exit 1
fi

cp "$IMAGE_PATH" ./disk_images/

IMAGE_NAME=$(basename "$IMAGE_PATH")

docker-compose run --rm forensic-analyzer \
    "/app/images/$IMAGE_NAME" \
    "$@"