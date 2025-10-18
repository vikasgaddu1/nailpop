# Deployment Guide - Wall Inspector

This guide covers deploying the Wall Inspector application to various platforms.

## Quick Deploy Options

### 1. Streamlit Community Cloud (FREE)

**Recommended for: MVP, demo, personal use**

1. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/yourusername/wall-inspector.git
   git push -u origin master
   ```

2. **Deploy on Streamlit Cloud**:
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Configure Secrets** (for Google Drive):
   - Go to your app dashboard
   - Click "Settings" → "Secrets"
   - Add your Google Drive credentials

**Limits**: 
- 1GB RAM
- Public repositories only
- Community support

### 2. Render (FREE Tier)

**Recommended for: Production MVP, private repos**

1. **Create `render.yaml`**:
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

2. **Deploy**:
   - Connect GitHub to Render
   - Create new Web Service
   - Select repository
   - Deploy automatically

**Limits**:
- 512MB RAM
- Spins down after 15 minutes of inactivity
- 750 hours/month free

### 3. Railway (FREE $5 Credit)

**Recommended for: Better performance, always-on**

1. **Connect Railway to GitHub**
2. **Auto-detected Python app**
3. **Set environment variables**
4. **Deploy**

**Limits**:
- $5/month credit
- Better performance than Render
- No sleep mode

## Production Deployment

### 1. Google Cloud Run

**Recommended for: Scalable production**

1. **Create Dockerfile**:
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   COPY . .
   
   RUN pip install uv
   RUN uv sync
   
   EXPOSE 8080
   CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]
   ```

2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy wall-inspector --source .
   ```

**Cost**: Pay-per-use, very cost-effective

### 2. AWS ECS/Fargate

**Recommended for: Enterprise, AWS ecosystem**

1. **Push Docker image to ECR**
2. **Create ECS task definition**
3. **Deploy to Fargate**

### 3. DigitalOcean App Platform

**Recommended for: Simple production**

1. **Connect GitHub**
2. **Auto-detected Python app**
3. **$5/month for basic tier**

## Environment Configuration

### Required Environment Variables

```bash
# Optional: Google Drive Integration
GOOGLE_DRIVE_CREDENTIALS=<service-account-json>
GOOGLE_DRIVE_FOLDER_ID=<folder-id>

# Optional: Custom configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Streamlit Secrets (secrets.toml)

```toml
[google_drive]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "service-account@project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/service-account%40project.iam.gserviceaccount.com"

google_drive_folder_id = "your-folder-id"
```

## Google Drive Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "wall-inspector"
3. Enable Google Drive API

### 2. Create Service Account

1. Navigate to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Name: "wall-inspector-service"
4. Create and download JSON key

### 3. Setup Drive Folder

1. Create folder in Google Drive: "WallInspections"
2. Share folder with service account email
3. Copy folder ID from URL
4. Add to secrets configuration

## Performance Optimization

### 1. Image Processing
- Resize images to max 1920x1920 before processing
- Use WebP format for better compression
- Implement client-side compression

### 2. Model Caching
- Models are cached using `@st.cache_resource`
- Consider using external model hosting for large models

### 3. Memory Management
- Clear session state when needed
- Optimize OpenCV operations
- Use streaming for large files

## Monitoring and Analytics

### 1. Streamlit Analytics
- Built-in usage statistics
- User interaction tracking

### 2. Google Analytics (Optional)
Add to `app.py`:
```python
# Google Analytics tracking
st.components.v1.html("""
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
""")
```

## Security Considerations

### 1. API Keys
- Never commit secrets to git
- Use environment variables or secrets management
- Rotate keys regularly

### 2. File Upload Security
- Validate file types and sizes
- Scan uploaded files for malware
- Implement rate limiting

### 3. Data Privacy
- Images are processed locally by default
- Google Drive integration requires user consent
- Consider GDPR compliance for EU users

## Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   uv sync  # Reinstall dependencies
   ```

2. **Memory Issues**:
   - Reduce image size
   - Clear session state
   - Use lighter models

3. **Google Drive Errors**:
   - Check service account permissions
   - Verify folder sharing
   - Validate JSON credentials

4. **Mobile Issues**:
   - Test on actual devices
   - Check viewport meta tag
   - Validate touch interactions

### Debug Mode

Run with debug logging:
```bash
uv run streamlit run app.py --logger.level debug
```

## Cost Estimates

| Platform | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| Streamlit Cloud | ✅ Unlimited | N/A | MVP/Demo |
| Render | 750 hrs/month | $7/month | Development |
| Railway | $5 credit | $5+/month | Production |
| Google Cloud Run | 2M requests | Pay-per-use | Scale |
| DigitalOcean | N/A | $5/month | Simple prod |

## Next Steps

1. **Deploy to Streamlit Cloud** for immediate testing
2. **Setup Google Drive** for sharing functionality  
3. **Test on mobile devices** thoroughly
4. **Consider upgrading** to paid tier for production use
5. **Add analytics** to track usage patterns
6. **Implement feedback system** for model improvement

## Support

For deployment issues:
- Check Streamlit documentation
- Review platform-specific guides
- Open GitHub issues for bugs
- Contact platform support for hosting issues
