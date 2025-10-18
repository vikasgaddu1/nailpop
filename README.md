# Wall Inspector

AI-powered wall damage detection web application built with Streamlit. Mobile-first design for easy on-site inspections.

## Features

- **Mobile-First Design**: Simple 2-tap workflow from photo to results
- **AI-Powered Detection**: Automatically detect:
  - Cracks in walls (Canny edge detection, CLAHE enhancement)
  - Nail pops (HoughCircles algorithm)
  - Water damage (HSV/LAB color analysis)
  - Color inconsistencies
- **Three Analysis Modes**:
  - Basic Computer Vision (free, runs locally)
  - OpenAI GPT-4o Vision (professional analysis)
  - Google Gemini 2.5 Flash (fast AI analysis)
- **Visual Annotations**: Color-coded overlays showing detected defects with severity ratings
- **Easy Sharing**:
  - Download annotated images and JSON reports
  - Google Drive integration (optional)
  - Shareable links for contractors

## Quick Start

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Run the application**:
   ```bash
   uv run streamlit run app.py
   ```

3. **Open in browser**:
   - **Local**: `http://localhost:8501`
   - **Mobile** (same WiFi): `http://YOUR-LOCAL-IP:8501`

## Usage

### Simple 2-Step Workflow

1. **Choose AI Model**: Select Basic (free), OpenAI, or Gemini
   - Enter API key if using AI analysis (optional)

2. **Take or Upload Photo**:
   - Mobile: Camera or gallery (native controls)
   - Desktop: File picker
   - Analysis starts automatically
   - View results with annotated image

3. **Take Another Photo** or download results

### Detection Legend

- 🔴 **Red lines**: Detected cracks
- 🟢 **Green circles**: Potential nail pops
- 🔵 **Blue overlay**: Water damage (dark areas)
- 🟡 **Yellow overlay**: Color inconsistencies

## Documentation

- **[Deployment Guide](docs/DEPLOYMENT.md)** - Deploy to Streamlit Cloud, Render, or Google Cloud Run
- **[Development Guide](docs/DEVELOPMENT.md)** - Local development, testing, and contributing
- **[Changelog](docs/CHANGELOG.md)** - Version history and migration notes

## Technical Stack

- **Framework**: Streamlit
- **Computer Vision**: OpenCV
- **Image Processing**: PIL/Pillow
- **Package Management**: UV
- **AI Providers**: OpenAI GPT-4o, Google Gemini 2.5 Flash

## Deployment

Quick deploy to Streamlit Community Cloud (free):

1. Push to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Deploy `app.py`

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions and other platforms.

## Development

```bash
# Install dependencies
uv sync

# Run locally
uv run streamlit run app.py

# Test on mobile (same WiFi)
# Open http://YOUR-LOCAL-IP:8501
```

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for full development guide.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on mobile devices
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open a GitHub issue.
