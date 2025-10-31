# Quick Vercel Deployment Guide

## Step 1: Fix the Environment Variable Error

The error you're seeing is because Next.js automatically handles `NEXT_PUBLIC_*` variables.

**In Vercel Dashboard:**

1. Go to your project settings
2. Click on "Environment Variables"
3. Add a new variable:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: Your backend URL (e.g., `https://your-backend.com/api/v1`)
   - Make sure to select all environments (Production, Preview, Development)
4. Click "Save"

## Step 2: Redeploy

After adding the environment variable:

1. Go to "Deployments" tab
2. Click on the three dots next to your latest deployment
3. Select "Redeploy"
4. Check "Use existing Build Cache" (optional)
5. Click "Redeploy"

## Step 3: Verify

Once deployed:
1. Visit your Vercel URL
2. Open browser console (F12)
3. Check if the frontend is connecting to your backend API
4. Test by asking a question

## Common Issues

### If you see "Invalid request" error:
- Make sure `NEXT_PUBLIC_API_URL` is set correctly
- The value should NOT include `/chat` at the end
- Example: `https://api.yourdomain.com/api/v1` ✅
- Not: `https://api.yourdomain.com/api/v1/chat` ❌

### If you see CORS errors:
Update your backend `config.py` to allow your Vercel domain:
```python
CORS_ORIGINS = [
    "http://localhost:3000",
    "https://your-app.vercel.app",
]
```

## What Changed in Your Code

1. **Removed** the `env` object from `next.config.js` - Next.js handles `NEXT_PUBLIC_*` automatically
2. **Removed** `vercel.json` - Not needed for Next.js (auto-detected)
3. Environment variable is read directly from `process.env.NEXT_PUBLIC_API_URL`

## Testing Locally

To test with your production API locally:

1. Create `.env.local` in frontend folder:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-api.com/api/v1
   ```

2. Run:
   ```bash
   npm run dev
   ```

That's it! Your frontend should now deploy successfully on Vercel.
