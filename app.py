"""
Wall Inspector - Mobile-First Version
AI-powered wall damage detection optimized for mobile devices
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
from datetime import datetime
import hashlib

# Import detection models and services
from models import CrackDetector, NailPopDetector, ColorAnalyzer
from services import get_drive_service, is_drive_available, get_available_providers, analyze_with_ai

# Configure page for mobile
st.set_page_config(
    page_title="Wall Inspector",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Mobile-optimized CSS
st.markdown("""
<style>
    /* Mobile-first design */
    .main > div {
        padding-top: 1rem;
        max-width: 800px;
        margin: 0 auto;
    }
    
    /* Large, thumb-friendly buttons */
    .stButton > button {
        width: 100%;
        min-height: 56px;
        font-size: 1.2rem;
        font-weight: 600;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* File uploader styling */
    .stFileUploader {
        width: 100%;
    }
    
    .stFileUploader > div > button {
        width: 100%;
        min-height: 56px;
        font-size: 1.2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
    }
    
    /* Header styling */
    .app-header {
        text-align: center;
        padding: 1rem 0 2rem 0;
    }
    
    .app-header h1 {
        margin-bottom: 0.5rem;
    }
    
    /* Responsive images */
    img {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_detection_models():
    """Load detection models once"""
    return {
        'crack_detector': CrackDetector(),
        'nail_pop_detector': NailPopDetector(),
        'color_analyzer': ColorAnalyzer()
    }

def analyze_wall_image(image):
    """Perform computer vision analysis"""
    models = load_detection_models()
    
    crack_results = models['crack_detector'].detect_cracks(image)
    nail_pop_results = models['nail_pop_detector'].detect_nail_pops(image)
    color_results = models['color_analyzer'].analyze_color_consistency(image)
    
    return crack_results, nail_pop_results, color_results

def create_comprehensive_annotation(image, crack_results, nail_pop_results, color_results):
    """Create annotated image with all detected issues"""
    try:
        models = load_detection_models()
        annotated = np.array(image).copy()
        
        # Add overlays
        try:
            annotated = models['color_analyzer'].create_color_overlay(annotated, color_results)
        except Exception as e:
            print(f"Color overlay failed: {e}")
        
        try:
            annotated = models['crack_detector'].draw_cracks(annotated, crack_results)
        except Exception as e:
            print(f"Crack annotation failed: {e}")
        
        try:
            annotated = models['nail_pop_detector'].draw_nail_pops(annotated, nail_pop_results)
        except Exception as e:
            print(f"Nail pop annotation failed: {e}")
        
        return annotated
    except Exception as e:
        print(f"Annotation failed: {e}")
        return np.array(image)

def main():
    # Header
    st.markdown("""
    <div class="app-header">
        <h1>🏠 Wall Inspector</h1>
        <p>Mobile-first AI wall damage detection</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'last_analyzed_hash' not in st.session_state:
        st.session_state.last_analyzed_hash = None
    if 'ai_analysis_mode' not in st.session_state:
        st.session_state.ai_analysis_mode = 'Basic Computer Vision'
    if 'openai_api_key' not in st.session_state:
        try:
            st.session_state.openai_api_key = st.secrets.get('OPENAI_API_KEY', '')
        except:
            st.session_state.openai_api_key = ''
    if 'gemini_api_key' not in st.session_state:
        try:
            st.session_state.gemini_api_key = st.secrets.get('GEMINI_API_KEY', '')
        except:
            st.session_state.gemini_api_key = ''
    
    # STEP 1: AI Model Selection
    st.markdown("### 🧠 Choose Analysis Method")
    
    analysis_mode = st.radio(
        "Select how you want to analyze your wall:",
        [
            "🔧 Basic Computer Vision (Free)",
            "🤖 OpenAI GPT-4o Vision (Pro)",
            "🔮 Google Gemini 2.5 Flash (Pro)"
        ],
        key="analysis_mode",
        help="Basic is free. AI models provide professional assessment."
    )
    
    # Update session state
    if analysis_mode.startswith("🤖"):
        st.session_state.ai_analysis_mode = "OpenAI GPT-4V"
    elif analysis_mode.startswith("🔮"):
        st.session_state.ai_analysis_mode = "Google Gemini"
    else:
        st.session_state.ai_analysis_mode = "Basic Computer Vision"
    
    # API Key Configuration (only for AI models)
    if st.session_state.ai_analysis_mode != "Basic Computer Vision":
        with st.expander("🔑 Configure API Key", expanded=not st.session_state.get('openai_api_key') and not st.session_state.get('gemini_api_key')):
            if st.session_state.ai_analysis_mode == "OpenAI GPT-4V":
                openai_key = st.text_input(
                    "OpenAI API Key:",
                    type="password",
                    value=st.session_state.openai_api_key,
                    help="Get from https://platform.openai.com/api-keys",
                    placeholder="sk-..."
                )
                st.session_state.openai_api_key = openai_key.strip() if openai_key else ""
                
                if openai_key:
                    st.success("✅ API key configured")
                else:
                    st.warning("⚠️ Please enter your API key to use AI analysis")
            
            elif st.session_state.ai_analysis_mode == "Google Gemini":
                gemini_key = st.text_input(
                    "Gemini API Key:",
                    type="password",
                    value=st.session_state.gemini_api_key,
                    help="Get from https://aistudio.google.com/app/apikey",
                    placeholder="AIza..."
                )
                cleaned_key = gemini_key.strip().rstrip('\\') if gemini_key else ""
                st.session_state.gemini_api_key = cleaned_key
                
                if gemini_key:
                    st.success("✅ API key configured")
                else:
                    st.warning("⚠️ Please enter your API key to use AI analysis")
    
    st.markdown("---")
    
    # STEP 2: Photo Capture
    st.markdown("### 📸 Take Photo")
    st.info("💡 **Mobile**: Tap button to open camera or select from gallery")
    
    # File uploader - on mobile this gives option to use camera or gallery
    uploaded_file = st.file_uploader(
        "📱 Take or Upload Photo",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=False,
        key="photo_upload",
        help="On mobile: Opens camera or gallery. On desktop: Choose file.",
        label_visibility="visible"
    )
    
    # STEP 3: Auto-Analysis
    if uploaded_file is not None:
        # Calculate hash to detect new images
        image_bytes = uploaded_file.getvalue()
        image_hash = hashlib.md5(image_bytes).hexdigest()
        
        # Check if this is a new image
        if image_hash != st.session_state.last_analyzed_hash:
            # New image - auto-analyze
            st.session_state.last_analyzed_hash = image_hash
            image = Image.open(uploaded_file)
            
            # Check API key requirements
            can_analyze = True
            error_msg = ""
            
            if st.session_state.ai_analysis_mode == "OpenAI GPT-4V" and not st.session_state.openai_api_key:
                can_analyze = False
                error_msg = "Please configure your OpenAI API key above"
            elif st.session_state.ai_analysis_mode == "Google Gemini" and not st.session_state.gemini_api_key:
                can_analyze = False
                error_msg = "Please configure your Gemini API key above"
            
            if not can_analyze:
                st.error(f"❌ {error_msg}")
                st.session_state.analysis_complete = False
            else:
                # AUTO-ANALYZE
                with st.spinner(f"⏳ Analyzing with {st.session_state.ai_analysis_mode}..."):
                    try:
                        # Basic CV analysis
                        crack_results, nail_pop_results, color_results = analyze_wall_image(image)
                        
                        basic_analysis = {
                            'cracks': max(0, crack_results.get('count', 0)),
                            'crack_severity': crack_results.get('severity', 'None'),
                            'crack_length': max(0, crack_results.get('total_length', 0)),
                            'nail_pops': max(0, nail_pop_results.get('count', 0)),
                            'nail_pop_severity': nail_pop_results.get('severity', 'None'),
                            'water_damage_pixels': max(0, color_results.get('water_damage_pixels', 0)),
                            'color_inconsistency_pixels': max(0, color_results.get('color_inconsistency_pixels', 0)),
                            'color_severity': color_results.get('severity', 'None')
                        }
                        
                    except Exception as e:
                        st.error(f"⚠️ Analysis error: {str(e)}")
                        crack_results = {'count': 0, 'severity': 'None', 'total_length': 0, 'contours': []}
                        nail_pop_results = {'count': 0, 'severity': 'None', 'circles': []}
                        color_results = {'water_damage_pixels': 0, 'color_inconsistency_pixels': 0, 'severity': 'None', 'dark_areas': None, 'unusual_saturation': None}
                        basic_analysis = {
                            'cracks': 0, 'crack_severity': 'None', 'crack_length': 0,
                            'nail_pops': 0, 'nail_pop_severity': 'None',
                            'water_damage_pixels': 0, 'color_inconsistency_pixels': 0, 'color_severity': 'None'
                        }
                    
                    # AI analysis if selected
                    ai_analysis = None
                    if st.session_state.ai_analysis_mode != "Basic Computer Vision":
                        try:
                            providers = get_available_providers(
                                openai_key=st.session_state.openai_api_key,
                                gemini_key=st.session_state.gemini_api_key
                            )
                            
                            if st.session_state.ai_analysis_mode == "OpenAI GPT-4V" and "OpenAI GPT-4V" in providers:
                                ai_analysis = analyze_with_ai(providers["OpenAI GPT-4V"], image, basic_analysis)
                            elif st.session_state.ai_analysis_mode == "Google Gemini" and "Google Gemini" in providers:
                                ai_analysis = analyze_with_ai(providers["Google Gemini"], image, basic_analysis)
                        except Exception as e:
                            st.error(f"❌ AI analysis failed: {str(e)}")
                    
                    # Create annotated image
                    annotated_image = create_comprehensive_annotation(
                        image, crack_results, nail_pop_results, color_results
                    )
                    
                    # Store results
                    st.session_state.analysis_complete = True
                    st.session_state.detected_issues = basic_analysis
                    st.session_state.ai_analysis = ai_analysis
                    st.session_state.annotated_image = annotated_image
                    st.session_state.original_image = image
                    st.session_state.crack_results = crack_results
                    st.session_state.nail_pop_results = nail_pop_results
                    st.session_state.color_results = color_results
                
                st.success("✅ Analysis complete!")
        
        # Display results if available
        if st.session_state.analysis_complete and st.session_state.get('annotated_image') is not None:
            st.markdown("---")
            st.markdown("### 📊 Analysis Results")
            
            # Show images
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Original")
                st.image(st.session_state.original_image, width="stretch")
            with col2:
                st.markdown("#### Detected Issues")
                st.image(st.session_state.annotated_image, width="stretch")
            
            # Metrics
            issues = st.session_state.detected_issues
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🔴 Cracks", issues['cracks'], delta=issues['crack_severity'])
            with col2:
                st.metric("🟢 Nail Pops", issues['nail_pops'], delta=issues['nail_pop_severity'])
            with col3:
                st.metric("🔵 Water Damage", f"{issues['water_damage_pixels']} px")
            with col4:
                st.metric("🟡 Color Issues", f"{issues['color_inconsistency_pixels']} px")
            
            # AI Analysis results
            if st.session_state.get('ai_analysis') and st.session_state.ai_analysis.get('success'):
                st.markdown("#### 🤖 Professional Analysis")
                with st.expander("View detailed assessment", expanded=True):
                    st.markdown(st.session_state.ai_analysis.get('professional_notes', 'No detailed notes available'))
            
            # Action buttons
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📸 Take Another Photo", use_container_width=True, key="take_another"):
                    st.session_state.analysis_complete = False
                    st.session_state.last_analyzed_hash = None
                    st.rerun()
            with col2:
                # Convert annotated image to bytes for download
                img_byte_arr = io.BytesIO()
                Image.fromarray(st.session_state.annotated_image).save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                st.download_button(
                    label="💾 Download Report",
                    data=img_byte_arr,
                    file_name=f"wall_inspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png",
                    use_container_width=True,
                    key="download_report"
                )

if __name__ == "__main__":
    main()

