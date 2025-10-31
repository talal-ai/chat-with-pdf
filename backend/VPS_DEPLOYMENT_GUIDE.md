# AAOIFI Chatbot Backend - VPS Server Deployment Guide

## 📋 Prerequisites
- VPS server with SSH access (5.189.174.219)
- Python 3.11+ installed
- Root or sudo access

## 🚀 Step-by-Step Deployment

### 1. Upload Backend to Server

Upload the entire `backend` folder to `/var/www/backend` using one of these methods:

**Option A: Using SCP (from your local machine)**
```bash
scp -r backend root@5.189.174.219:/var/www/
```

**Option B: Using Git**
```bash
ssh root@5.189.174.219
cd /var/www
git clone https://github.com/talal-ai/chat-with-pdf.git
mv chat-with-pdf/backend .
```

**Option C: Using SFTP/FileZilla**
- Connect to: `5.189.174.219`
- Upload `backend` folder to `/var/www/`

### 2. SSH into Your Server

```bash
ssh root@5.189.174.219
```

### 3. Run Deployment Script

```bash
cd /var/www/backend
chmod +x deploy_server.sh
./deploy_server.sh
```

This will:
- ✅ Create virtual environment at `/var/www/backend/.venv`
- ✅ Install all Python dependencies
- ✅ Set up necessary folders and permissions

### 4. Create `.env` File

```bash
cd /var/www/backend
nano .env
```

Paste your environment variables:
```properties
# LLM Provider
LLM_PROVIDER=groq

# Groq Settings
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.3

# OpenAI Settings (optional)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.7

# Pinecone Settings
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=aaoifi-standards

# API Configuration
DEBUG=False
```

Save with `Ctrl+X`, then `Y`, then `Enter`.

### 5. Test Run the Server

```bash
cd /var/www/backend
chmod +x start_production.sh
./start_production.sh
```

Your API should now be running at: `http://5.189.174.219:5015`

Test it: `http://5.189.174.219:5015/api/v1/health`

Press `Ctrl+C` to stop.

### 6. Set Up as System Service (Auto-start)

```bash
# Copy service file
cp /var/www/backend/aaoifi-chatbot.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable service (start on boot)
systemctl enable aaoifi-chatbot

# Start service
systemctl start aaoifi-chatbot

# Check status
systemctl status aaoifi-chatbot
```

### 7. Manage the Service

```bash
# Start
systemctl start aaoifi-chatbot

# Stop
systemctl stop aaoifi-chatbot

# Restart
systemctl restart aaoifi-chatbot

# View logs
journalctl -u aaoifi-chatbot -f
```

## 🔐 Firewall Configuration

Make sure port 5015 is open:

```bash
# For UFW
ufw allow 5015/tcp

# For firewalld
firewall-cmd --permanent --add-port=5015/tcp
firewall-cmd --reload

# For iptables
iptables -A INPUT -p tcp --dport 5015 -j ACCEPT
```

## 🌐 Access Your API

- **Health Check**: `http://5.189.174.219:5015/api/v1/health`
- **API Base URL**: `http://5.189.174.219:5015/api/v1`

## 🔄 Updating Your Backend

When you make changes:

```bash
# SSH into server
ssh root@5.189.174.219

# Navigate to backend
cd /var/www/backend

# Pull latest changes (if using Git)
git pull

# Or upload files via SCP/SFTP

# Activate environment and reinstall dependencies
source .venv/bin/activate
pip install -r requirements.txt

# Restart service
systemctl restart aaoifi-chatbot
```

## 🔧 Alternative: Run with Gunicorn (Recommended)

For better production stability:

```bash
cd /var/www/backend
chmod +x start_gunicorn.sh
./start_gunicorn.sh
```

Or update the systemd service to use `start_gunicorn.sh`.

## 📊 Monitoring

View real-time logs:
```bash
journalctl -u aaoifi-chatbot -f
```

Check if server is running:
```bash
systemctl status aaoifi-chatbot
```

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Find process using port 5015
lsof -i :5015
# Kill the process
kill -9 <PID>
```

### Permission Denied
```bash
chmod -R 755 /var/www/backend
chown -R root:root /var/www/backend
```

### Service Won't Start
```bash
# Check logs
journalctl -u aaoifi-chatbot -n 50
```

### Dependencies Not Installing
```bash
cd /var/www/backend
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

## 🎯 Next Steps

After backend is running on your VPS:

1. Update frontend `.env.production`:
   ```
   NEXT_PUBLIC_API_URL=http://5.189.174.219:5015/api/v1
   ```

2. Deploy frontend to Vercel with this backend URL

3. (Optional) Set up Nginx reverse proxy for HTTPS support

## 📝 Summary

Your backend is now deployed at:
- **API URL**: `http://5.189.174.219:5015/api/v1`
- **Health Check**: `http://5.189.174.219:5015/api/v1/health`
- **Logs**: `journalctl -u aaoifi-chatbot -f`
- **Auto-starts**: On server reboot via systemd service
