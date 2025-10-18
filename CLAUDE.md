# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Wall Inspector is an AI-powered wall damage detection web application built with Streamlit. It analyzes images to detect cracks, nail pops, water damage, and color inconsistencies using computer vision and optional AI analysis (OpenAI GPT-4V or Google Gemini 2.5 Flash).

## Development Commands

### Environment Setup
```bash
# Install dependencies using UV package manager
uv sync

# Run the application locally
uv run streamlit run app.py

# The app will be available at http://localhost:8501
```

### Testing
The project uses basic computer vision algorithms without a formal test suite. Manual testing workflow:
1. Run the app with `uv run streamlit run app.py`
2. Test with different image types (mobile camera, file upload, enhanced camera)
3. Verify detection results on the annotated images
4. Test AI providers if API keys are configured

### Deployment
See DEPLOYMENT.md for detailed deployment instructions. Key platforms:
- **Streamlit Community Cloud**: Free tier, recommended for demos
- **Render**: Free tier with auto-deploy from GitHub
- **Google Cloud Run**: Production-ready, pay-per-use

## Architecture Overview

### Application Structure

**Main Entry Point**: `app.py`
- Streamlit web application with mobile-first responsive design
- Handles image capture (simple camera, enhanced multi-camera, file upload)
- Orchestrates analysis pipeline: computer vision → AI analysis (optional) → annotation
- Manages session state and UI rendering
- Implements Google Drive sharing functionality

**Detection Models**: `models/crack_detector.py`
Three core computer vision classes:
- `CrackDetector`: Uses Canny edge detection, CLAHE enhancement, and morphological operations to identify cracks
- `NailPopDetector`: Implements HoughCircles algorithm to detect circular nail pop patterns
- `ColorAnalyzer`: Analyzes HSV/LAB color spaces to detect water damage and color inconsistencies

**AI Providers**: `services/ai_providers.py`
- `AIProvider`: Base class for external AI analysis
- `OpenAIProvider`: GPT-4V integration for professional building inspection analysis
- `GeminiProvider`: Google Gemini 2.5 Flash integration
- Both providers encode images to base64, send structured prompts, and parse professional assessments

**Cloud Storage**: `services/google_drive.py`
- `GoogleDriveService`: Handles OAuth2 service account authentication
- Creates folders, uploads images/reports, generates shareable links
- Supports both Streamlit secrets and credentials file initialization

**Camera Component**: `components/camera_selector.py`
- Custom Streamlit component with HTML/JavaScript
- Enumerates available cameras (front/back on mobile, integrated/external on desktop)
- Captures high-resolution images with camera metadata
- Uses bidirectional communication between JavaScript and Python via postMessage

### Key Design Patterns

**Error Handling Strategy**:
- All detection methods use try/except with safe fallback values
- Image processing errors return original images rather than failing
- API failures degrade gracefully to basic computer vision results
- Dimension mismatches are handled with automatic resizing

**Session State Management**:
- `st.session_state` stores captured images, analysis results, API keys, camera info
- Enables multi-step workflows (capture → analyze → save/share)
- Prevents re-running expensive operations on page refreshes

**Analysis Pipeline**:
1. Image capture (camera or upload)
2. Basic computer vision analysis (always runs, provides metrics)
3. Optional AI analysis (requires API key, enhances basic results)
4. Annotation overlay creation (layers crack/nail pop/color overlays)
5. Results display with metrics and recommendations
6. Save/share functionality (Google Drive or local download)

## Important Implementation Details

### Image Processing
- All images converted to numpy arrays for OpenCV operations
- Preprocessing includes Gaussian blur, CLAHE enhancement, and colorspace conversions
- Canny edge detection uses adaptive thresholds based on image median
- Contour filtering based on aspect ratio (>3 for cracks) and compactness (<0.3)
- Color overlays use weighted blending (80% original, 20% overlay)

### AI Integration
- Images resized to max 1024px to reduce API costs
- Minimum 32px enforced to avoid API errors
- JPEG format with 85% quality for optimal compression
- Structured prompts include basic CV results for context
- JSON response parsing with text fallback for robustness

### Mobile Optimization
- CSS media queries for responsive design at 768px breakpoint
- PWA-style app header and styling
- Touch-optimized controls (larger buttons, min-height 3rem)
- Camera component auto-selects back camera on mobile devices
- Resolution detection with quality recommendations (8MP+ excellent, 4-8MP good)

### Google Drive Integration
- Service account authentication (not OAuth user flow)
- Creates timestamped folders: `WallInspection_{name}_{timestamp}`
- Uploads 3 files: original image, annotated image, JSON report
- Sets public permissions for sharing with contractors
- Graceful degradation to local download if Drive unavailable

## Common Workflows

### Adding a New Detection Algorithm
1. Create a new class in `models/crack_detector.py` (or new file in `models/`)
2. Implement detection method returning dict with `count`, `severity`, and detection data
3. Add assessment method to calculate severity based on metrics
4. Implement drawing method to annotate detected features
5. Update `analyze_wall_image()` in `app.py` to call new detector
6. Update `create_comprehensive_annotation()` to include new annotations
7. Add new metrics to results display in main UI

### Adding a New AI Provider
1. Create new class inheriting from `AIProvider` in `services/ai_providers.py`
2. Implement `encode_image()` for provider's format requirements
3. Implement `analyze_wall_image()` with provider-specific API calls
4. Add provider to `get_available_providers()` function
5. Update UI in `app.py` to include new provider option
6. Add API key input field in AI Analysis Settings expander

### Modifying the Camera Component
1. Edit HTML/JavaScript in `components/camera_selector.py`
2. Update `enumerateCameras()` for camera detection logic
3. Modify `startCamera()` constraints for resolution/quality changes
4. Update `captureData` structure if adding new metadata
5. Adjust `process_camera_result()` to handle new data fields
6. Test on both mobile and desktop browsers

## Configuration Files

- `pyproject.toml`: Python package metadata and dependencies (UV format)
- `uv.lock`: Locked dependency versions for reproducible builds
- `.streamlit/secrets.toml`: Google Drive credentials and API keys (not in repo)
- `credentials.json`: Alternative Google Drive credentials file (not in repo)

## API Key Management

The app supports three analysis modes:
1. **Basic Computer Vision** (default, no API key required)
2. **OpenAI GPT-4V** (requires OpenAI API key from platform.openai.com)
3. **Google Gemini 2.5 Flash** (requires Gemini API key from aistudio.google.com)

API keys are stored in `st.session_state` and never persisted. Users enter them via expanders in the UI. For deployment, consider using Streamlit secrets for pre-configured keys.

## Known Limitations

- Enhanced camera component is experimental and may fail on some browsers
- Nail pop detection has false positives on textured walls
- Color analysis thresholds tuned for white/light-colored walls
- Google Drive requires service account setup (not user OAuth)
- AI analysis costs money per image (basic CV is free)

## Dependencies

Core libraries:
- **streamlit**: Web framework and UI components
- **opencv-python**: Computer vision algorithms (Canny, Hough, morphological ops)
- **pillow**: Image handling and conversions
- **numpy**: Array operations and image data
- **google-api-python-client**: Google Drive API integration
- **requests**: HTTP client for AI provider APIs
