#!/bin/bash
# Deployment script for FastAPI backend on your VPS server
# Run this script after uploading the backend folder to /var/www/

set -e  # Exit on error

echo "🚀 Starting backend deployment..."

# Navigate to backend directory
cd /var/www/backend

# Check Python version
echo "📌 Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Set permissions
echo "🔐 Setting permissions..."
chmod +x deploy_server.sh
chmod -R 755 /var/www/backend

echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Create/update .env file with your API keys"
echo "2. Start the server with: ./start_production.sh"
echo "   Or manually: source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 5015"
