# Development Guide

Guide for local development and testing of Wall Inspector.

## Setup

### Prerequisites

- Python 3.11 or higher
- [UV package manager](https://github.com/astral-sh/uv)
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/wall-inspector.git
   cd wall-inspector
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Run the application:**
   ```bash
   uv run streamlit run app.py
   ```

4. **Open in browser:**
   - Local: `http://localhost:8501`
   - Mobile (same WiFi): `http://YOUR-LOCAL-IP:8501`

## Project Structure

```
wall-inspector/
├── app.py                      # Main application (mobile-first)
├── models/
│   └── crack_detector.py       # CV detection algorithms
├── services/
│   ├── ai_providers.py         # OpenAI/Gemini integration
│   └── google_drive.py         # Cloud storage
├── components/
│   └── camera_selector.py      # Camera component (legacy)
├── docs/                       # Documentation
│   ├── DEPLOYMENT.md           # Deployment guide
│   ├── DEVELOPMENT.md          # This file
│   └── CHANGELOG.md            # Version history
├── .streamlit/
│   └── secrets.toml.template   # Secrets template
├── requirements.txt            # Production dependencies
├── pyproject.toml              # UV package config
└── README.md                   # Project overview
```

## Development Workflow

### Running Locally

```bash
# Standard run
uv run streamlit run app.py

# With debug logging
uv run streamlit run app.py --logger.level debug

# Custom port
uv run streamlit run app.py --server.port 8502
```

### Testing

The project uses manual testing (no automated test suite yet).

#### Basic Testing Workflow

1. **Run the app:**
   ```bash
   uv run streamlit run app.py
   ```

2. **Test image capture:**
   - Click "Take or Upload Photo"
   - Test with different image types:
     - Mobile camera photos
     - File uploads
     - Various resolutions (low to high)

3. **Test detection algorithms:**
   - Upload test images with known defects
   - Verify detection accuracy
   - Check annotation overlays

4. **Test AI providers (if API keys configured):**
   - Test with OpenAI GPT-4o
   - Test with Google Gemini 2.5 Flash
   - Compare results with Basic CV

5. **Test mobile responsiveness:**
   - Open on actual mobile device
   - Test on different screen sizes using browser DevTools
   - Verify touch interactions

#### Mobile Device Testing

1. **Find your local IP:**
   ```bash
   # Windows
   ipconfig

   # Mac/Linux
   ifconfig
   ```

2. **Access from mobile (same WiFi):**
   ```
   http://YOUR-LOCAL-IP:8501
   ```

3. **Test mobile-specific features:**
   - Camera access
   - File upload from gallery
   - Touch interactions
   - Responsive layout
   - Auto-analysis workflow

### API Configuration

#### Local Development

Create `.streamlit/secrets.toml` (not committed to git):

```toml
# Optional: OpenAI API key
OPENAI_API_KEY = "sk-your-key-here"

# Optional: Google Gemini API key
GEMINI_API_KEY = "your-key-here"

# Optional: Google Drive integration
[google_drive]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "service-account@project.iam.gserviceaccount.com"
# ... (full service account JSON)
```

Alternatively, enter API keys directly in the app UI (stored in session state only).

## Making Changes

### Adding a New Detection Algorithm

1. **Create detector class** in [models/crack_detector.py](../models/crack_detector.py):
   ```python
   class NewDetector:
       def detect(self, image):
           """Detect defects and return results dict"""
           return {
               "count": 0,
               "severity": "none",
               "data": []
           }

       def assess_severity(self, results):
           """Calculate severity based on results"""
           return "none"  # or "minor", "moderate", "severe"

       def draw_annotations(self, image, results):
           """Draw annotations on image"""
           return image
   ```

2. **Update analysis pipeline** in [app.py](../app.py):
   ```python
   # In analyze_wall_image()
   detector = NewDetector()
   new_results = detector.detect(image)
   issues["new_defect"] = new_results
   ```

3. **Add annotations** to overlay:
   ```python
   # In create_comprehensive_annotation()
   annotated = detector.draw_annotations(annotated, issues["new_defect"])
   ```

4. **Display results** in UI

### Adding a New AI Provider

1. **Create provider class** in [services/ai_providers.py](../services/ai_providers.py):
   ```python
   class NewAIProvider(AIProvider):
       def __init__(self, api_key):
           self.api_key = api_key

       def analyze_wall_image(self, image, basic_results):
           """Send image to AI and return analysis"""
           # Implementation here
           pass
   ```

2. **Update provider selection** in [app.py](../app.py):
   ```python
   if selected_model == "New AI":
       provider = NewAIProvider(api_key)
   ```

3. **Add API key input** in UI

### Modifying UI/UX

The app is **mobile-first** with these design principles:

- **Single-column layout** (centered)
- **Large touch targets** (minimum 3rem height)
- **Auto-analysis** (no manual "Analyze" button)
- **Minimal options** (progressive disclosure)
- **Native controls** (file uploader for camera/gallery)

When making UI changes:
1. Test on mobile device first
2. Ensure touch targets are large enough
3. Minimize scrolling
4. Use clear visual feedback
5. Test on various screen sizes

## Code Style

### Python

- Follow PEP 8
- Use type hints where helpful
- Add docstrings for public functions
- Keep functions focused and short

### Streamlit

- Use `st.session_state` for state management
- Cache expensive operations with `@st.cache_resource`
- Clear, descriptive button labels
- Provide user feedback (spinners, success/error messages)

### Error Handling

- Use try/except blocks for all external API calls
- Graceful degradation (fall back to basic features)
- Clear error messages for users
- Safe defaults (return original image if processing fails)

## Performance Tips

### Image Processing

- Images auto-resize to max 1024px for AI analysis
- Use OpenCV efficiently (minimize copies)
- Cache detection models
- Process in RGB colorspace when possible

### Session State

- Store only necessary data in session state
- Clear old results when starting new analysis
- Use hash-based duplicate detection

### API Calls

- Compress images before sending (JPEG 85% quality)
- Include basic CV results in AI prompts (better context)
- Handle rate limits gracefully

## Debugging

### Enable Debug Logging

```bash
uv run streamlit run app.py --logger.level debug
```

### Common Issues

**Issue: Import errors**
```bash
# Reinstall dependencies
uv sync
```

**Issue: OpenCV errors**
```bash
# Windows may need Visual C++ Redistributable
# Mac may need: brew install opencv
```

**Issue: Session state not persisting**
- Check for `st.rerun()` calls
- Verify state initialization in `if 'key' not in st.session_state`

**Issue: Image processing fails**
- Check image format (JPEG, PNG supported)
- Verify image is not corrupted
- Check file size (very large images may timeout)

## Git Workflow

### Branching

```bash
# Create feature branch
git checkout -b feature/new-detector

# Make changes, commit
git add .
git commit -m "feat: add new defect detector"

# Push and create PR
git push origin feature/new-detector
```

### Commit Messages

Follow conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting)
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Build/tooling changes

### Before Pushing

1. Test locally
2. Test on mobile device
3. Check for console errors
4. Verify no secrets committed
5. Update documentation if needed

## Dependencies

### Core Libraries

- **streamlit** - Web framework
- **opencv-python** - Computer vision (local dev)
- **opencv-python-headless** - Computer vision (cloud deployment)
- **pillow** - Image handling
- **numpy** - Array operations

### Optional Dependencies

- **google-api-python-client** - Google Drive integration
- **requests** - HTTP client for AI APIs

### Managing Dependencies

```bash
# Add new dependency
uv add package-name

# Update dependencies
uv sync

# Update requirements.txt for cloud deployment
uv pip compile pyproject.toml -o requirements.txt
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Test on mobile devices
5. Update documentation
6. Submit pull request

## Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [OpenCV Documentation](https://docs.opencv.org)
- [UV Package Manager](https://github.com/astral-sh/uv)
- [Python Best Practices](https://peps.python.org/pep-0008/)
