#!/bin/bash
# Production startup script for FastAPI backend
# Run this after deploy_server.sh

set -e

echo "🚀 Starting FastAPI backend in production mode..."

# Navigate to backend directory
cd /var/www/backend

# Activate virtual environment
source .venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️ Warning: .env file not found!"
    echo "Please create .env file with your API keys before starting."
    exit 1
fi

# Start Uvicorn
echo "✅ Starting server on 0.0.0.0:5015..."
uvicorn app.main:app --host 0.0.0.0 --port 5015 --workers 2
