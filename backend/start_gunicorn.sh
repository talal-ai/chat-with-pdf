#!/bin/bash
# Production startup script using Gunicorn (recommended for production)
# Gunicorn provides better process management and worker handling

set -e

echo "🚀 Starting FastAPI backend with Gunicorn..."

# Navigate to backend directory
cd /var/www/aaoifi-chatbot-backend

# Activate virtual environment
source .venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️ Warning: .env file not found!"
    echo "Please create .env file with your API keys before starting."
    exit 1
fi

# Start Gunicorn with Uvicorn workers
echo "✅ Starting server on 0.0.0.0:5015 with Gunicorn..."
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:5015 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
