# 🚀 Render Deployment Guide - InsightEngine

## Prerequisites
✅ GitHub repository with latest code
✅ Render account (sign up at render.com)

## 🎯 Deploy Both Frontend & Backend to Render

### Step 1: Deploy Backend (Web Service)

1. **Go to [render.com](https://render.com) and sign in with GitHub**
2. **Click "New +" → "Web Service"**
3. **Connect your `Data-Analyst-Agent` repository**
4. **Configure Backend:**
   ```
   Name: insightengine-backend
   Root Directory: backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Instance Type: Free
   ```

5. **Add Environment Variables:**
   ```
   GEMINI_API_KEY = AIzaSyAEMFabEcS3aOUSwVuM38Jj55cWOIqfJYw
   ```

6. **Click "Create Web Service"**
7. **Wait for deployment** (5-10 minutes)
8. **Copy your backend URL**: `https://insightengine-backend.onrender.com`

### Step 2: Deploy Frontend (Static Site)

1. **Click "New +" → "Static Site"**
2. **Connect same `Data-Analyst-Agent` repository**
3. **Configure Frontend:**
   ```
   Name: insightengine-frontend
   Root Directory: front-end
   Build Command: npm run build
   Publish Directory: front-end/dist
   ```

4. **Add Environment Variables:**
   ```
   VITE_API_URL = https://insightengine-backend.onrender.com
   ```
   (Replace with your actual backend URL from Step 1)

5. **Click "Create Static Site"**
6. **Wait for deployment** (2-3 minutes)

### Step 3: Test Your App

1. **Visit your frontend URL**: `https://insightengine-frontend.onrender.com`
2. **Test data upload and analysis**
3. **Check that frontend connects to backend properly**

## 🎯 URLs You'll Get

- **Frontend**: `https://insightengine-frontend.onrender.com`
- **Backend API**: `https://insightengine-backend.onrender.com`
- **API Docs**: `https://insightengine-backend.onrender.com/docs`

## 🔧 Advantages of This Setup

✅ **750 free hours/month** for backend
✅ **Unlimited static hosting** for frontend  
✅ **Single platform** - easier management
✅ **Auto-deployments** from GitHub
✅ **Built-in HTTPS** and custom domains
✅ **Integrated monitoring** and logs
✅ **Better performance** than serverless

## 🚨 Important Notes

- **Cold starts**: Free tier apps sleep after 15 minutes of inactivity
- **Wake up time**: ~30 seconds for first request after sleep
- **Auto-deploy**: Any push to GitHub main branch triggers new deployment
- **Environment variables**: Can be updated in Render dashboard

## 📊 Monitoring

- **Logs**: Available in each service dashboard
- **Metrics**: CPU, memory, and request stats
- **Alerts**: Set up notifications for failures

Your InsightEngine is now fully deployed on Render! 🎉