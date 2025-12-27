#!/bin/bash

WORKERS=${WORKERS:-4}
BIND=${BIND:-0.0.0.0:8000}

echo "Starting Gunicorn with $WORKERS workers and binding to $BIND"

gunicorn app.main:app \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind $BIND \
    --timeout 120