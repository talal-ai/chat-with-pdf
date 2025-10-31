#!/bin/bash
# Startup script for Render deployment
# Render sets PORT environment variable automatically

# Use PORT from environment, default to 10000 if not set
PORT=${PORT:-10000}

echo "Starting server on port $PORT"
uvicorn app.main:app --host 0.0.0.0 --port $PORT
