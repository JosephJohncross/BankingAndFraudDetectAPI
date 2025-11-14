#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# Correct Flower command
FLOWER_CMD="celery -A backend.app.core.celery_app \
    flower \
    --broker=${CELERY_BROKER_URL} \
    --address=0.0.0.0 \
    --port=5555 \
    --basic_auth=${CELERY_FLOWER_USER}:${CELERY_FLOWER_PASSWORD}"

# Run directly, DO NOT wrap Celery inside watchfiles
exec sh -c "$FLOWER_CMD"
