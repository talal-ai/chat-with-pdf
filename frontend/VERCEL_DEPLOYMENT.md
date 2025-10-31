# AAOIFI Chatbot Frontend - Vercel Deployment Guide

## ✅ Pre-Deployment Checklist

- [x] Backend deployed at: `https://aaoifi-chatbot-backend.onrender.com`
- [x] Frontend configured for production
- [x] Environment variables ready
- [x] Build configuration verified
- [x] Next.js package.json has correct scripts
- [x] .env.production created with production API URL

## 🚀 Quick Deploy (Recommended Method)

### Method 1: Import from GitHub (Easiest)

1. **Go to Vercel**: <https://vercel.com/new>

2. **Import Repository**:
   - Click "Import Git Repository"
   - Select `talal-ai/chat-with-pdf`
   - Click "Import"

3. **Configure Project**:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: Click "Edit" → Select `frontend` folder
   - **Build & Development Settings**: (auto-detected, no changes needed)
     - Build Command: `npm run build`
     - Output Directory: `.next`
     - Install Command: `npm install`

4. **Add Environment Variable**:
   - Click "Environment Variables"
   - Add:
     - **Name**: `NEXT_PUBLIC_API_URL`
     - **Value**: `https://aaoifi-chatbot-backend.onrender.com/api/v1`
     - **Environments**: Check all (Production, Preview, Development)

5. **Click "Deploy"** and wait 2-3 minutes

### Method 2: Using Vercel CLI

```bash
# Install Vercel CLI globally
npm install -g vercel

# Navigate to frontend folder
cd frontend

# Login to Vercel
vercel login

# Deploy to production
vercel --prod
```

When prompted:
- Set up and deploy? → **Y**
- Which scope? → Select your account
- Link to existing project? → **N**
- Project name? → `aaoifi-chatbot` (or your choice)
- In which directory is your code located? → `./` (already in frontend)
- Want to override settings? → **N**

### 3. Set Environment Variables in Vercel

In your Vercel project settings → Environment Variables, add:

| Name | Value | Environment |
|------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | `https://aaoifi-chatbot-backend.onrender.com/api/v1` | Production, Preview, Development |

**Important**: 
- ✅ The variable name MUST start with `NEXT_PUBLIC_` to be accessible in the browser
- ✅ Include `/api/v1` at the end of the backend URL
- ✅ Use `https://` (not `http://`)

### 4. Deploy

Click **Deploy** and wait for the build to complete (usually 2-3 minutes).

## 🔧 Troubleshooting

### Build Fails
- Check that `frontend` is set as the root directory
- Verify all dependencies are in `package.json`
- Check build logs for specific errors

### API Connection Issues
- Verify `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- Test backend URL directly: `https://aaoifi-chatbot-backend.onrender.com/api/v1/health`
- Check CORS settings in backend (should already allow all origins)

### Environment Variable Not Working
- Ensure variable name starts with `NEXT_PUBLIC_`
- Redeploy after adding environment variables
- Check browser console for the actual API URL being used

## 📝 Post-Deployment

After successful deployment, you'll get a URL like:
- `https://your-project.vercel.app`

Test the following:
1. ✅ Homepage loads
2. ✅ Can send messages to chatbot
3. ✅ Can upload PDFs
4. ✅ Conversations are saved
5. ✅ Settings dialog works

## 🔄 Future Updates

To deploy updates:
```bash
git add .
git commit -m "your changes"
git push
```

Vercel will automatically rebuild and deploy on every push to `main` branch.

## 🌐 URLs

- **Frontend**: `https://your-project.vercel.app` (after deployment)
- **Backend**: `https://aaoifi-chatbot-backend.onrender.com`
- **Backend API**: `https://aaoifi-chatbot-backend.onrender.com/api/v1`
- **Health Check**: `https://aaoifi-chatbot-backend.onrender.com/api/v1/health`
