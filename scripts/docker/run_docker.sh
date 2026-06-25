#!/bin/bash

set -euo pipefail

docker run \
    --rm \
    --name codeclaw \
    --env-file .env \
    codeclaw:latest
