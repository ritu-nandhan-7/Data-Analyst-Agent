# 🚀 Vercel Deployment Guide

## Prerequisites
1. GitHub repository (✅ Done)
2. Vercel account (sign up at vercel.com)

## Deployment Steps

### Option 1: Deploy Both Frontend & Backend (Recommended)

1. **Go to [Vercel.com](https://vercel.com)**
2. **Connect GitHub** - Sign in with your GitHub account
3. **Import Repository** - Select `Data-Analyst-Agent` (InsightEngine)
4. **Configure Project:**
   - **Framework Preset**: Detect automatically (Vite)
   - **Root Directory**: `front-end` (for frontend)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. **Environment Variables** (Add these in Vercel dashboard):
   ```
   VITE_API_URL=https://your-backend-domain.vercel.app
   ```

6. **Deploy Backend Separately:**
   - Create new Vercel project
   - Select same repository
   - Set **Root Directory**: `backend`
   - Add environment variables:
     ```
     GEMINI_API_KEY=your_gemini_api_key
     ```

### Option 2: Deploy Frontend Only (Simpler)

1. **Deploy Frontend to Vercel**
2. **Keep Backend Local** - Run locally and use ngrok for public URL
3. **Update VITE_API_URL** to your ngrok URL

## Files Created for Deployment

✅ `vercel.json` - Root project configuration
✅ `front-end/vercel.json` - Frontend configuration  
✅ `backend/vercel.json` - Backend configuration
✅ `backend/requirements.txt` - Updated with versions
✅ `backend/runtime.txt` - Python version specification
✅ `front-end/.env.example` - Environment variables template

## Environment Variables Needed

### Frontend
- `VITE_API_URL` - Backend API URL

### Backend  
- `GEMINI_API_KEY` - Your Google Gemini API key
- Any other API keys you're using

## Next Steps

1. Commit all changes to GitHub
2. Go to Vercel and import your repository
3. Configure environment variables
4. Deploy!

## Testing
After deployment, your app will be available at:
- Frontend: `https://your-project-name.vercel.app`
- Backend: `https://your-backend-name.vercel.app`