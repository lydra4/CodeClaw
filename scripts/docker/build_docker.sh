#!/bin/bash

set -euo pipefail

docker build \
    -f docker/codeclaw.Dockerfile \
    -t codeclaw .
