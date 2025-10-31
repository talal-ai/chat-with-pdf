# 🚀 Quick Deployment Instructions

You're currently at: `/var/www/aaoifi-chatbot-backend`

## Step 1: Run Deployment Script

```bash
chmod +x deploy_server.sh start_production.sh start_gunicorn.sh
./deploy_server.sh
```

This will:
- ✅ Create Python virtual environment (`.venv`)
- ✅ Install all dependencies from `requirements.txt`
- ✅ Set up uploads directory
- ✅ Set correct permissions

## Step 2: Create `.env` File

```bash
nano .env
```

Paste your configuration:

```properties
# LLM Provider
LLM_PROVIDER=groq

# Groq Settings
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.3

# OpenAI Settings (optional)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.3

# Pinecone Settings
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=aaoifi-standards

# Embedding Settings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# API Configuration
DEBUG=False
```

Save: `Ctrl+X` → `Y` → `Enter`

## Step 3: Start Production Server

### Option A: With Gunicorn (Recommended for Production)
```bash
./start_gunicorn.sh
```

### Option B: With Uvicorn
```bash
./start_production.sh
```

## Step 4: Test Your API

```bash
# In another terminal
curl http://localhost:5015/api/v1/health
```

Or visit in browser: `http://YOUR_SERVER_IP:5015/api/v1/health`

## 📊 Server is Running!

- **API Base URL**: `http://YOUR_SERVER_IP:5015/api/v1`
- **Health Check**: `http://YOUR_SERVER_IP:5015/api/v1/health`
- **Docs**: `http://YOUR_SERVER_IP:5015/docs`

## 🔄 To Stop Server

Press `Ctrl+C`

## 🔧 Troubleshooting

### Check Python version:
```bash
python3 --version  # Should be 3.11+
```

### If port 5015 is busy:
```bash
lsof -i :5015
kill -9 <PID>
```

### View logs:
```bash
tail -f logs/app.log  # If logging to file
```

### Reinstall dependencies:
```bash
source .venv/bin/activate
pip install -r requirements.txt --no-cache-dir
```

## 🔐 Open Firewall (if needed)

```bash
# UFW
ufw allow 5015/tcp

# Firewalld
firewall-cmd --permanent --add-port=5015/tcp
firewall-cmd --reload
```

## 🎯 Set Up Systemd Service (Auto-start on Boot)

After testing that the server works, set it up as a system service:

```bash
# Copy service file to systemd
cp aaoifi-chatbot.service /etc/systemd/system/

# Reload systemd to recognize new service
systemctl daemon-reload

# Enable service (auto-start on boot)
systemctl enable aaoifi-chatbot

# Start the service
systemctl start aaoifi-chatbot

# Check status
systemctl status aaoifi-chatbot
```

### Managing the Service:

```bash
# Start
systemctl start aaoifi-chatbot

# Stop
systemctl stop aaoifi-chatbot

# Restart
systemctl restart aaoifi-chatbot

# View logs
journalctl -u aaoifi-chatbot -f

# Check status
systemctl status aaoifi-chatbot
```

## 🎯 Summary

Your server configuration:
- **Path**: `/var/www/aaoifi-chatbot-backend`
- **Port**: `5015`
- **Workers**: 4 (Gunicorn) or 2 (Uvicorn)
- **Environment**: Production mode

Ready to deploy! 🚀
