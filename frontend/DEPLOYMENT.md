# Frontend Deployment Guide - Vercel

## 🚀 Quick Deploy to Vercel

### Prerequisites
- GitHub account
- Vercel account (sign up at https://vercel.com)
- Your backend API must be deployed and accessible

---

## ⚠️ IMPORTANT: Environment Variable Setup

In Vercel, you **MUST** set this environment variable:

**Key:** `NEXT_PUBLIC_API_URL`  
**Value:** `https://your-backend-api.com/api/v1` (your production backend URL without `/chat`)

Example: `https://api.mydomain.com/api/v1`

---

### Method 1: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare frontend for Vercel deployment"
   git push origin main
   ```

2. **Go to Vercel**:
   - Visit https://vercel.com
   - Click "Add New Project"
   - Import your GitHub repository

3. **Configure the Project**:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-filled)
   - **Output Directory**: `.next` (auto-filled)

4. **Add Environment Variable**:
   - Click "Environment Variables"
   - Add:
     - Name: `NEXT_PUBLIC_API_URL`
     - Value: `https://your-backend-api.com/api/v1` (your production backend URL)
   - Add for all environments (Production, Preview, Development)

5. **Deploy**:
   - Click "Deploy"
   - Wait 2-3 minutes for deployment to complete
   - You'll get a URL like `https://your-app.vercel.app`

### Method 2: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Navigate to frontend folder**:
   ```bash
   cd frontend
   ```

3. **Login to Vercel**:
   ```bash
   vercel login
   ```

4. **Deploy**:
   ```bash
   vercel
   ```
   
   Follow the prompts:
   - Set up and deploy? `Y`
   - Which scope? Select your account
   - Link to existing project? `N`
   - What's your project's name? `aaoifi-chatbot-frontend`
   - In which directory is your code located? `./`
   - Want to override the settings? `N`

5. **Set Environment Variable**:
   ```bash
   vercel env add NEXT_PUBLIC_API_URL
   ```
   Enter your backend URL when prompted.

6. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

### Method 3: One-Click Deploy

Click this button (after setting up your repo):

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/YOUR_REPO)

## 🔧 Post-Deployment Configuration

### 1. Update Backend CORS Settings

Your backend needs to allow requests from your Vercel domain. Update `backend/app/core/config.py`:

```python
# Add your Vercel domain to allowed origins
CORS_ORIGINS = [
    "http://localhost:3000",
    "https://your-app.vercel.app",  # Add this
    "https://your-custom-domain.com"  # If you have a custom domain
]
```

### 2. Test Your Deployment

1. Visit your Vercel URL
2. Try asking a question
3. Check if the API connection works
4. Test file upload functionality
5. Test different conversation tones

### 3. Set Up Custom Domain (Optional)

1. Go to your Vercel project settings
2. Click "Domains"
3. Add your custom domain
4. Follow the DNS configuration instructions
5. Wait for DNS propagation (5-60 minutes)

## 🔄 Automatic Deployments

Vercel automatically deploys:
- **Production**: Every push to `main` branch
- **Preview**: Every push to other branches or pull requests

## 📊 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `https://api.yourdomain.com/api/v1` |

## 🐛 Troubleshooting

### API Connection Fails
- Check if `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- Ensure backend CORS allows your Vercel domain
- Check if backend is running and accessible

### Build Fails
- Check build logs in Vercel dashboard
- Run `npm run build` locally to test
- Ensure all dependencies are in `package.json`

### Environment Variable Not Working
- Environment variables must start with `NEXT_PUBLIC_` to be accessible in the browser
- Redeploy after adding environment variables
- Clear cache and redeploy if needed

## 📱 Local Development

To test with your production backend locally:

1. Create `.env.local`:
   ```bash
   NEXT_PUBLIC_API_URL=https://your-backend-api.com/api/v1
   ```

2. Run development server:
   ```bash
   npm run dev
   ```

## 🔐 Security Notes

- Never commit `.env.local` to Git (already in .gitignore)
- Use environment variables for all API URLs
- Keep sensitive data in environment variables only
- Review Vercel's security best practices

## 📞 Support

- Vercel Docs: https://vercel.com/docs
- Next.js Docs: https://nextjs.org/docs
- GitHub Issues: Your repository issues page

---

**Next Steps:**
1. Deploy your backend (if not already deployed)
2. Follow the deployment steps above
3. Update the `NEXT_PUBLIC_API_URL` with your backend URL
4. Test the deployment thoroughly
