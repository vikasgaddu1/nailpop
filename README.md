# Wall Inspector 🏠

AI-powered wall damage detection web application built with Streamlit for mobile-first experience.

## Features

- **Advanced Camera Selection**: 
  - Choose between multiple cameras (front/back on mobile, integrated/external on desktop)
  - Automatic detection of camera capabilities and resolution
  - Optimized for 4K webcams and high-resolution mobile cameras
  - Real-time camera switching and quality assessment
- **AI-Powered Detection**: Automatically detect:
  - Cracks in walls using advanced edge detection
  - Water damage and discoloration analysis
  - Color inconsistencies across wall surfaces
  - Potential nail pops using circular detection
- **Visual Annotations**: See detected issues highlighted on your images with severity indicators
- **Easy Sharing**: 
  - Google Drive integration for cloud sharing
  - Download annotated images and detailed JSON reports
  - Generate shareable links for contractors
- **Mobile Optimized**: 
  - PWA-style responsive design for smartphones and tablets
  - Touch-optimized controls and gestures
  - Optimized for both portrait and landscape orientations

## Quick Start

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Run the application**:

   **For Mobile/Tablet** (Recommended for phone users):
   ```bash
   uv run streamlit run app_mobile_optimized.py
   ```

   **For Desktop** (Full-featured version):
   ```bash
   uv run streamlit run app.py
   ```

3. **Open in browser**: Navigate to `http://localhost:8501`

> **💡 New**: We now offer a mobile-optimized version with step-by-step wizard interface! See [MOBILE_UX_GUIDE.md](MOBILE_UX_GUIDE.md) for details.

## Usage

### Mobile-Optimized Version (Recommended for phones/tablets)
1. **Step 1 - Capture**: Take a photo or upload from gallery
2. **Step 2 - Settings**: Choose analysis mode (Basic free or AI professional)
3. **Step 3 - Analyze**: Run the analysis with one tap
4. **Step 4 - Results**: View results in organized tabs (Images, Metrics, Save)

### Desktop Version (Full-featured)
1. **Select Camera**: Choose between enhanced camera (multi-camera support), simple camera, or file upload
2. **Camera Setup**:
   - **Mobile**: App automatically detects and recommends back camera for better quality
   - **Desktop**: Choose between integrated webcam or external 4K camera
   - **Quality Check**: App shows resolution and provides quality recommendations
3. **Capture Image**: Take photo with selected camera or upload from gallery
4. **Analyze**: Click "Analyze Wall Defects" to detect issues using AI
5. **Review Results**: View detected problems with visual annotations and severity ratings
6. **Save & Share**: Name your inspection and share via Google Drive or download locally

> **Choose Your Version**: Mobile version = less scrolling (60% reduction), step-by-step guidance, tabbed results. Desktop version = all features visible, side-by-side comparison, advanced camera options.

## Detection Capabilities

### Current Features
- **Crack Detection**: Uses edge detection to identify potential cracks
- **Color Analysis**: Detects areas with unusual brightness or saturation
- **Circular Detection**: Identifies potential nail pops using Hough circles

### Detection Legend
- 🔴 **Red lines**: Detected cracks
- 🔵 **Blue areas**: Potential water damage (dark areas)
- 🟡 **Yellow areas**: Color inconsistencies
- 🟢 **Green circles**: Potential nail pops

## Technical Stack

- **Framework**: Streamlit for rapid web app development
- **Computer Vision**: OpenCV for image processing
- **Image Processing**: PIL/Pillow for image handling
- **Package Management**: UV for dependency management

## Future Enhancements

- [ ] Google Drive integration for cloud storage
- [ ] Advanced ML models for better detection accuracy
- [ ] Interactive annotation tools
- [ ] Contractor sharing system
- [ ] Historical inspection tracking

## Deployment

### Local Development
```bash
uv run streamlit run app.py
```

### Production Deployment
- **Streamlit Community Cloud**: Free hosting for public repos
- **Render**: Free tier with automatic deployments
- **Heroku**: Simple deployment with git integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on mobile devices
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open a GitHub issue or contact the development team.
