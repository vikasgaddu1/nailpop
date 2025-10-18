# Wall Inspector 🏠

AI-powered wall damage detection web application built with Streamlit for mobile-first experience.

## Features

- **Mobile Camera Integration**: Take photos directly from your mobile device
- **AI-Powered Detection**: Automatically detect:
  - Cracks in walls
  - Water damage and discoloration
  - Color inconsistencies
  - Potential nail pops
- **Visual Annotations**: See detected issues highlighted on your images
- **Easy Sharing**: Download annotated images and analysis reports
- **Mobile Optimized**: Responsive design for smartphones and tablets

## Quick Start

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Run the application**:
   ```bash
   uv run streamlit run app.py
   ```

3. **Open in browser**: Navigate to `http://localhost:8501`

## Usage

1. **Capture Image**: Use your mobile camera or upload from gallery
2. **Analyze**: Click "Analyze Wall Defects" to detect issues
3. **Review Results**: View detected problems with visual annotations
4. **Save & Share**: Name your inspection and download results

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
