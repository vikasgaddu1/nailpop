# Changelog

All notable changes to Wall Inspector are documented here.

## [Current] - Mobile-First Version

### Features
- ✅ Mobile-first design with auto-analysis workflow
- ✅ Single-button photo capture (native camera/gallery)
- ✅ AI model selection before photo capture
- ✅ Automatic analysis on photo upload
- ✅ Hash-based duplicate detection
- ✅ Quick restart with "Take Another Photo" button
- ✅ Simplified UI with minimal options
- ✅ Three analysis modes:
  - Basic Computer Vision (free)
  - OpenAI GPT-4o Vision
  - Google Gemini 2.5 Flash

### Detection Capabilities
- Crack detection (Canny edge detection, CLAHE enhancement)
- Nail pop detection (HoughCircles algorithm)
- Water damage detection (HSV/LAB color analysis)
- Color inconsistency detection
- Severity assessment (none/minor/moderate/severe)

### User Experience
- 2-tap workflow (photo → auto-results)
- Large touch targets (56px buttons)
- Responsive design for mobile/tablet/desktop
- Native camera controls (zoom, flash, focus)
- Download annotated results (PNG)
- Google Drive sharing (optional)

---

## Version History

### Mobile-First Redesign (October 2025)

**Major Changes:**
- Replaced multi-mode camera selection with single native file uploader
- Removed manual "Analyze" button (auto-analysis on upload)
- Added hash-based image change detection
- Moved AI model selection to top of interface
- Simplified workflow from 4-5 taps to 2 taps
- Removed legacy camera selector component

**Files:**
- Replaced `app.py` with mobile-first version
- Archived old version as `app_with_multiple_modes.py`
- Removed experimental `app_mobile_v2.py`

**Impact:**
- 60% reduction in user actions
- Cleaner, more intuitive interface
- Better mobile browser compatibility

### Multi-Step Wizard Version (Archived)

**Features (no longer in use):**
- 4-step wizard interface (Capture → Settings → Analyze → Results)
- Progress bar with visual feedback
- Tabbed results display
- Multiple camera modes (Simple/Enhanced/Gallery)

**Why Changed:**
- Enhanced camera mode had browser compatibility issues
- Manual analyze button was redundant
- Multiple camera options confused users
- Wizard added unnecessary steps

**Files Removed:**
- `app_mobile_optimized.py`
- `MOBILE_UX_GUIDE.md`
- `MOBILE_IMPROVEMENTS_SUMMARY.md`
- `QUICK_TEST.md`

### Bug Fixes

#### JSON Serialization Error (Fixed)

**Issue:**
- App crashed when saving reports with NumPy data types
- TypeError: Object of type int64 is not JSON serializable

**Solution:**
- Added `convert_to_serializable()` helper function
- Recursively converts NumPy types to native Python types
- Fixed in both mobile and desktop versions

**Files Modified:**
- `app.py`
- `app_mobile_optimized.py` (archived)

### Deployment Improvements

**Streamlit Cloud Compatibility:**
- Created `requirements.txt` with `opencv-python-headless`
- Updated `pyproject.toml` for cloud deployment
- Added `packages.txt` for OpenCV system dependencies
- Created `.streamlit/secrets.toml.template`
- Updated app to auto-load API keys from secrets

**Documentation:**
- Consolidated deployment guides
- Added troubleshooting tips
- Created mobile testing instructions

---

## Previous Features (No Longer Supported)

### Enhanced Camera Component

**What it was:**
- Custom Streamlit component with JavaScript
- Enumerated available cameras (front/back)
- Supported camera switching
- Provided resolution information

**Why removed:**
- Browser compatibility issues (especially mobile Safari)
- Permission handling problems
- Native file uploader is more reliable
- Modern browsers provide camera/gallery choice automatically

### Manual Analysis Button

**What it was:**
- Users had to click "Analyze Wall Defects" after capturing photo

**Why removed:**
- Redundant step (users always want analysis)
- Auto-analysis is faster and more intuitive
- Reduces cognitive load

### Multiple Camera Modes

**What they were:**
- Simple Camera (basic Streamlit camera input)
- Enhanced Camera (custom component with camera selection)
- Upload from Gallery (file uploader)

**Why simplified:**
- Simple camera had reliability issues
- Enhanced camera had compatibility problems
- File uploader handles both camera and gallery on mobile
- One option reduces confusion

---

## Technical Improvements

### Performance
- Images auto-resize to 1024px for AI analysis (cost optimization)
- Session state caching prevents re-analysis
- Efficient OpenCV operations
- Cached detection models

### Error Handling
- Graceful API failure (fallback to Basic CV)
- Safe defaults (return original image if processing fails)
- Clear user error messages
- Validation for file types and sizes

### Security
- API keys in session state (not persisted)
- Secrets not committed to git
- File type validation
- No server-side data storage

---

## Known Limitations

### Current Version
- Native camera access requires HTTPS (local testing may need workarounds)
- Browser camera permissions must be granted
- AI analysis requires API keys (Basic CV is free)
- Google Drive requires service account setup

### Detection Algorithms
- Nail pop detection has false positives on textured walls
- Color analysis tuned for white/light-colored walls
- Edge detection may miss hairline cracks
- Lighting affects detection accuracy

---

## Future Roadmap

### Planned Features
- [ ] Offline mode (PWA with service worker)
- [ ] Batch analysis (multiple photos)
- [ ] Comparison mode (before/after repairs)
- [ ] Photo gallery view
- [ ] Export to PDF reports
- [ ] Automated testing suite

### Under Consideration
- [ ] Real-time AR overlay
- [ ] Voice commands
- [ ] Push notifications
- [ ] Dark mode
- [ ] Swipe gestures for navigation
- [ ] Contractor sharing system
- [ ] Historical inspection tracking

---

## Migration Notes

### From Multi-Step Wizard → Mobile-First

If you were using `app_mobile_optimized.py`:

**What changed:**
- No more 4-step wizard
- Single-page interface with auto-analysis
- File uploader instead of camera modes
- Immediate results display

**What stayed the same:**
- All detection algorithms
- AI provider support
- Google Drive integration
- Download functionality

### From Original Desktop App → Mobile-First

If you were using original `app.py`:

**What changed:**
- Simplified camera options
- Auto-analysis (no manual button)
- Mobile-first layout
- AI selection moved to top

**What stayed the same:**
- All core functionality
- Detection accuracy
- API integrations
- Results format

---

## Documentation Structure

Current documentation (post-consolidation):

```
docs/
├── DEPLOYMENT.md    # Deployment guide (all platforms)
├── DEVELOPMENT.md   # Local development and testing
└── CHANGELOG.md     # This file
```

Removed (outdated):
- `MOBILE_UX_GUIDE.md` - Described old wizard interface
- `MOBILE_IMPROVEMENTS_SUMMARY.md` - Summary of old changes
- `QUICK_TEST.md` - Testing guide for old version
- `BUGFIX_JSON_SERIALIZATION.md` - Historical bug fix
- `DEPLOYMENT_STATUS.md` - Redundant with DEPLOYMENT.md
- `MOBILE_DEPLOY.md` - Merged into DEPLOYMENT.md
- `MOBILE_VERSION_TEST.md` - Outdated testing guide
- `DEPLOYED_MOBILE_FIRST.md` - Status update (obsolete)

---

## Credits

- Built with [Streamlit](https://streamlit.io)
- Computer vision powered by [OpenCV](https://opencv.org)
- AI analysis via [OpenAI](https://openai.com) and [Google Gemini](https://ai.google.dev)
- Package management by [UV](https://github.com/astral-sh/uv)
