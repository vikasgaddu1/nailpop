# Deployment Guide

Complete guide for deploying Wall Inspector to production.

## Quick Start

### Option 1: Streamlit Community Cloud (Recommended)

**Best for:** Free hosting, easy setup, automatic deployments

1. **Push to GitHub:**
   ```bash
   git remote add origin https://github.com/yourusername/wall-inspector.git
   git push -u origin master
   ```

2. **Deploy on Streamlit Cloud:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Configure Secrets** (optional):
   - Go to app settings → Secrets
   - Add API keys:
   ```toml
   # Optional: Pre-configure API keys
   OPENAI_API_KEY = "sk-your-key-here"
   GEMINI_API_KEY = "your-key-here"

   # Optional: Google Drive integration
   [google_drive]
   type = "service_account"
   project_id = "your-project-id"
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   client_email = "service-account@project.iam.gserviceaccount.com"
   # ... (see Google Drive Setup section)
   ```

**Limits:**
- 1GB RAM, public repositories only
- App sleeps after inactivity (wakes on access)
- Community support

**Your app URL:** `https://[your-app-name].streamlit.app`

### Option 2: Render

**Best for:** Private repos, auto-deployments from GitHub

1. **Create `render.yaml`:**
   ```yaml
   services:
     - type: web
       name: wall-inspector
       env: python
       buildCommand: "uv sync"
       startCommand: "uv run streamlit run app.py --server.port $PORT --server.address 0.0.0.0"
       envVars:
         - key: PYTHON_VERSION
           value: "3.11"
   ```

2. **Deploy:**
   - Connect GitHub to Render
   - Create new Web Service
   - Select repository
   - Deploy automatically

**Limits:**
- 512MB RAM, spins down after 15 minutes of inactivity
- 750 hours/month free

### Option 3: Google Cloud Run

**Best for:** Production, scalability, pay-per-use

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app
   COPY . .

   RUN pip install uv
   RUN uv sync

   EXPOSE 8080
   CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]
   ```

2. **Deploy:**
   ```bash
   gcloud run deploy wall-inspector --source .
   ```

**Cost:** Pay-per-use (very cost-effective for low/medium traffic)

## Environment Configuration

### Required Files

1. **requirements.txt** (already in repo)
   - Python dependencies for cloud deployment
   - Uses `opencv-python-headless` for cloud compatibility

2. **packages.txt** (for OpenCV system dependencies)
   ```
   libgl1-mesa-glx
   libglib2.0-0
   libsm6
   libxext6
   libxrender-dev
   libgomp1
   ```

3. **.streamlit/secrets.toml** (not in repo - create for local testing)
   - Use the template at `.streamlit/secrets.toml.template`
   - Add your API keys and credentials

### Optional: Google Drive Integration

#### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "wall-inspector"
3. Enable Google Drive API

#### 2. Create Service Account

1. Navigate to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Name: "wall-inspector-service"
4. Create and download JSON key

#### 3. Setup Drive Folder

1. Create folder in Google Drive: "WallInspections"
2. Share folder with service account email
3. Copy folder ID from URL
4. Add to secrets configuration

## Mobile Testing

### Test on Your Phone

1. **Local Testing (same WiFi):**
   ```bash
   # Find your local IP
   ipconfig  # Windows
   ifconfig  # Mac/Linux

   # App will be at: http://YOUR-LOCAL-IP:8501
   ```

2. **Cloud Testing:**
   - Open your Streamlit Cloud URL on mobile browser
   - Test camera functionality
   - Verify analysis works
   - Check responsive design

### Expected Mobile Behavior

- **iOS Safari:** Shows "Take Photo" or "Photo Library"
- **Android Chrome:** Shows "Camera" or "Browse"
- **Both:** Native camera with zoom, flash, focus controls

### Mobile Best Practices

- Use good lighting when taking photos
- Hold phone steady to avoid blur
- Ensure stable internet for AI analysis
- Basic Computer Vision works offline (no API needed)

## Troubleshooting

### OpenCV Import Error

**Solution:**
- Ensure `packages.txt` is in root directory with system dependencies
- Check that `requirements.txt` uses `opencv-python-headless`
- Reboot app in Streamlit Cloud settings

### Camera Not Working

**Solution:**
- Ensure browser has camera permissions
- Try "Upload Photo" as alternative
- Use HTTPS (required for camera access on modern browsers)

### API Keys Not Working

**Solution:**
- Verify keys are correctly configured in Streamlit secrets
- Check API keys are valid and have credits
- Use Basic Computer Vision mode (free, no API key needed)

### App is Slow

**Solution:**
- Streamlit Community Cloud has resource limits
- Large images take longer to process
- Consider resizing images before analysis
- Use Basic CV mode for faster processing

### Deployment Failed

**Solution:**
- Check deployment logs in Streamlit Cloud dashboard
- Verify all dependencies in `requirements.txt`
- Ensure `packages.txt` is present
- Check that all code is committed and pushed

## Updating Your App

### Automatic Updates (Streamlit Cloud)

1. Commit and push changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin master
   ```

2. Streamlit Cloud auto-detects changes (2-3 minutes)

### Manual Reboot

- Click "Reboot app" in Streamlit Cloud settings for immediate restart

## Performance Optimization

### Image Processing
- Images auto-resize to max 1024px for AI analysis
- Use WebP format for better compression
- Client-side compression implemented

### Caching
- Detection models cached using `@st.cache_resource`
- Analysis results cached in session state
- No re-analysis on page refreshes

### Memory Management
- Session state cleared on "New Analysis"
- Efficient OpenCV operations
- Minimal dependencies

## Security

### API Keys
- ✅ Use Streamlit secrets for deployment
- ✅ Keep `.streamlit/secrets.toml` in `.gitignore`
- ❌ Never commit API keys to GitHub
- ❌ Never share API keys publicly

### File Upload Security
- File type validation implemented
- Size limits enforced
- Images processed locally

### Privacy
- Images processed locally by default
- Google Drive integration requires user action
- No data stored on server (session state only)

## Cost Information

| Platform | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| Streamlit Cloud | ✅ Unlimited apps | N/A | MVP/Demo |
| Render | 750 hrs/month | $7/month | Development |
| Railway | $5 credit | $5+/month | Production |
| Google Cloud Run | 2M requests/month | Pay-per-use | Scale |
| DigitalOcean | N/A | $5/month | Simple production |

### AI Analysis Costs
- **Basic Computer Vision:** FREE
- **OpenAI GPT-4o:** ~$0.01-0.03 per image
- **Google Gemini 2.5 Flash:** FREE tier, then ~$0.001-0.005 per image

## Support Resources

### Official Documentation
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit API Reference](https://docs.streamlit.io/library/api-reference)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Google Gemini API Docs](https://ai.google.dev/docs)

### Getting API Keys
- **OpenAI:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Google Gemini:** [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### Community
- [Streamlit Forum](https://discuss.streamlit.io/)
- Project GitHub Issues

## Deployment Checklist

- [ ] Code committed and pushed to GitHub
- [ ] `requirements.txt` and `packages.txt` in root
- [ ] `.gitignore` configured (secrets not committed)
- [ ] Streamlit Cloud account created
- [ ] App deployed and running
- [ ] Tested on mobile device
- [ ] API keys configured (optional)
- [ ] Google Drive setup (optional)
- [ ] Custom domain configured (optional)
- [ ] Monitoring/analytics added (optional)
