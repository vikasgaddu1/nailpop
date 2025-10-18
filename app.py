"""
Wall Inspector - AI-powered wall damage detection web app
Built with Streamlit for mobile-first experience
"""

import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import io
import base64
from datetime import datetime
import os
import json

# Import our enhanced detection models
from models import CrackDetector, NailPopDetector, ColorAnalyzer
from services import get_drive_service, is_drive_available, get_available_providers, analyze_with_ai
from components import camera_selector, process_camera_result

# Configure page for mobile optimization
st.set_page_config(
    page_title="Wall Inspector",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile optimization
st.markdown("""
<style>
    /* Mobile-first responsive design */
    .main > div {
        padding-top: 1rem;
    }
    
    /* Button styling for mobile */
    .stButton > button {
        width: 100%;
        height: 3.5rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Primary action button */
    .stButton > button[key="analyze_btn"] {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        font-size: 1.3rem;
        height: 4rem;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }
    
    /* Camera input styling */
    .stCameraInput > div {
        border: 3px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        margin: 1rem 0;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        border: 2px dashed #ccc;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
        background-color: #f8f9fa;
    }
    
    /* Metric cards */
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* Image containers */
    .stImage > img {
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Mobile responsive adjustments */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 1rem;
        }
        
        .stButton > button {
            height: 3rem;
            font-size: 1rem;
        }
        
        .stButton > button[key="analyze_btn"] {
            height: 3.5rem;
            font-size: 1.2rem;
        }
        
        /* Stack columns on mobile */
        .row-widget.stHorizontal {
            flex-direction: column;
        }
        
        /* Larger touch targets */
        .stSelectbox > div > div {
            min-height: 3rem;
        }
        
        .stTextInput > div > div > input {
            height: 3rem;
            font-size: 1.1rem;
        }
    }
    
    /* Loading spinner customization */
    .stSpinner > div {
        border-top-color: #FF6B6B !important;
    }
    
    /* Success/error message styling */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }
    
    /* Hide Streamlit menu and footer on mobile */
    @media (max-width: 768px) {
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
    }
    
    /* PWA-style app bar */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0 0 20px 20px;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Floating action button style for camera */
    .fab-camera {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        color: white;
        border: none;
        font-size: 1.5rem;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
        cursor: pointer;
        z-index: 1000;
        display: none; /* Show via JavaScript when needed */
    }
</style>
""", unsafe_allow_html=True)

# Initialize detection models
@st.cache_resource
def load_detection_models():
    """Load and cache detection models"""
    return {
        'crack_detector': CrackDetector(),
        'nail_pop_detector': NailPopDetector(),
        'color_analyzer': ColorAnalyzer()
    }

def analyze_wall_image(image):
    """Comprehensive wall analysis using enhanced models"""
    models = load_detection_models()
    
    # Perform all detections
    crack_results = models['crack_detector'].detect_cracks(image)
    nail_pop_results = models['nail_pop_detector'].detect_nail_pops(image)
    color_results = models['color_analyzer'].analyze_color_consistency(image)
    
    return crack_results, nail_pop_results, color_results

def create_comprehensive_annotation(image, crack_results, nail_pop_results, color_results):
    """Create comprehensive annotated image with all detected issues"""
    models = load_detection_models()
    
    # Start with original image
    annotated = np.array(image).copy()
    
    # Add color overlays first (as background)
    annotated = models['color_analyzer'].create_color_overlay(annotated, color_results)
    
    # Add crack annotations
    annotated = models['crack_detector'].draw_cracks(annotated, crack_results)
    
    # Add nail pop annotations
    annotated = models['nail_pop_detector'].draw_nail_pops(annotated, nail_pop_results)
    
    return annotated

def main():
    # Mobile-optimized header
    st.markdown("""
    <div class="app-header">
        <h1>🏠 Wall Inspector</h1>
        <p>AI-powered wall damage detection for mobile devices</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'detected_issues' not in st.session_state:
        st.session_state.detected_issues = []
    if 'camera_mode' not in st.session_state:
        st.session_state.camera_mode = 'enhanced'
    if 'captured_image' not in st.session_state:
        st.session_state.captured_image = None
    if 'camera_info' not in st.session_state:
        st.session_state.camera_info = {}
    if 'ai_analysis_mode' not in st.session_state:
        st.session_state.ai_analysis_mode = 'Basic Computer Vision'
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ''
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = ''
    
    # Image capture section
    st.markdown("### 📸 Capture or Upload Wall Image")
    
    # Camera selection guide
    with st.expander("📖 Camera Selection Guide", expanded=False):
        st.markdown("""
        **For Best Results:**
        
        🏠 **Desktop/Laptop Users:**
        - 📹 **External 4K Webcam**: Highest quality, best for detailed damage detection
        - 💻 **Built-in Camera**: Good for basic inspection, may have lower resolution
        
        📱 **Mobile Users:**
        - 📱 **Back Camera**: Higher resolution, better sensors, recommended for wall inspection
        - 🤳 **Front Camera**: Lower resolution, suitable for quick checks only
        
        **💡 Tips:**
        - Ensure good lighting (natural light preferred)
        - Hold device steady or use a tripod
        - Get close enough to see wall texture clearly
        - Avoid shadows and reflections
        - Higher megapixel count = better defect detection
        """)
    
    # AI Analysis Configuration (Mobile-friendly)
    with st.expander("🧠 AI Analysis Settings", expanded=False):
        st.markdown("**Choose your analysis method:**")
        
        # Analysis mode selection
        analysis_mode = st.radio(
            "Analysis Method:",
            [
                "🔧 Basic Computer Vision (Free)",
                "🤖 OpenAI GPT-4V (Requires API Key)",
                "🔮 Google Gemini Pro Vision (Requires API Key)"
            ],
            key="analysis_mode_radio",
            help="Basic analysis is free but limited. AI models provide professional-grade analysis."
        )
        
        # Update session state
        if analysis_mode.startswith("🤖"):
            st.session_state.ai_analysis_mode = "OpenAI GPT-4V"
        elif analysis_mode.startswith("🔮"):
            st.session_state.ai_analysis_mode = "Google Gemini Pro Vision"
        else:
            st.session_state.ai_analysis_mode = "Basic Computer Vision"
        
        # API Key inputs for external providers
        if st.session_state.ai_analysis_mode == "OpenAI GPT-4V":
            st.markdown("#### 🔑 OpenAI Configuration")
            openai_key = st.text_input(
                "OpenAI API Key:",
                type="password",
                value=st.session_state.openai_api_key,
                help="Get your API key from https://platform.openai.com/api-keys",
                placeholder="sk-..."
            )
            st.session_state.openai_api_key = openai_key
            
            if openai_key:
                st.success("✅ OpenAI API key configured")
                st.info("💡 **GPT-4V Benefits**: Professional building inspection analysis, detailed repair recommendations, cost estimates")
            else:
                st.warning("⚠️ Please enter your OpenAI API key to use GPT-4V analysis")
        
        elif st.session_state.ai_analysis_mode == "Google Gemini Pro Vision":
            st.markdown("#### 🔑 Google Gemini Configuration")
            gemini_key = st.text_input(
                "Gemini API Key:",
                type="password",
                value=st.session_state.gemini_api_key,
                help="Get your API key from https://makersuite.google.com/app/apikey",
                placeholder="AIza..."
            )
            st.session_state.gemini_api_key = gemini_key
            
            if gemini_key:
                st.success("✅ Gemini API key configured")
                st.info("💡 **Gemini Benefits**: Advanced visual analysis, detailed damage assessment, practical repair advice")
            else:
                st.warning("⚠️ Please enter your Gemini API key to use Gemini Pro Vision analysis")
        
        else:
            st.info("🔧 **Basic Analysis**: Uses computer vision algorithms for crack, nail pop, and color analysis. Free but limited compared to AI models.")
    
    # Camera mode selection
    camera_mode = st.radio(
        "Choose capture method:",
        ["📱 Simple Camera", "📷 Enhanced Camera (Multi-camera support)", "📁 Upload from Gallery"],
        key="camera_mode_radio",
        horizontal=True
    )
    
    # Add note about enhanced camera
    if camera_mode == "📷 Enhanced Camera (Multi-camera support)":
        st.warning("⚠️ **Note**: Enhanced camera is experimental. If you have issues, please use Simple Camera mode.")
    
    uploaded_file = None
    
    if camera_mode == "📷 Enhanced Camera (Multi-camera support)":
        st.markdown("#### 🎥 Advanced Camera Selection")
        st.info("💡 **Tip**: Use back camera on mobile or external 4K camera on desktop for best quality")
        
        # Enhanced camera selector
        camera_result = camera_selector()
        
        # Process camera result if it's valid
        if camera_result and isinstance(camera_result, dict):
            image, camera_info = process_camera_result(camera_result)
            if image:
                # Store the captured image
                st.session_state.captured_image = image
                st.session_state.camera_info = camera_info
                st.session_state.analysis_complete = False  # Reset analysis state
                uploaded_file = "camera_capture"  # Flag to indicate camera capture
                
                st.success("📸 Photo captured successfully!")
                
                # Show camera info
                if camera_info:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📷 Camera", camera_info.get('name', 'Unknown'))
                    with col2:
                        st.metric("📐 Resolution", camera_info.get('resolution', 'Unknown'))
                    with col3:
                        st.metric("📱 Facing", camera_info.get('facing', 'Unknown'))
        
        # Check if we have a previously captured image
        elif st.session_state.captured_image is not None:
            uploaded_file = "camera_capture"  # Use previously captured image
            st.info("📸 Using previously captured image. Capture a new photo above to replace it.")
            
            if st.button("🗑️ Clear Captured Image", key="clear_image"):
                st.session_state.captured_image = None
                st.session_state.camera_info = {}
                st.session_state.analysis_complete = False
                st.rerun()
    
    elif camera_mode == "📱 Simple Camera":
        st.markdown("#### 📱 Simple Camera Capture")
        # Standard Streamlit camera input
        uploaded_file = st.camera_input("Take a picture of the wall", key="simple_camera")
    
    else:  # Upload from Gallery
        st.markdown("#### 📁 File Upload")
        uploaded_file = st.file_uploader(
            "Choose an image from your device",
            type=['png', 'jpg', 'jpeg', 'webp'],
            key="file_upload",
            help="Supported formats: PNG, JPG, JPEG, WebP. Max size: 200MB"
        )
    
    if uploaded_file is not None:
        # Handle different image sources
        if uploaded_file == "camera_capture":
            # Use captured image from enhanced camera
            image = st.session_state.captured_image
        else:
            # Use uploaded file or simple camera
            image = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Original Image")
            st.image(image, use_container_width=True)
            
            # Show image quality info
            img_width, img_height = image.size
            megapixels = (img_width * img_height) / 1_000_000
            
            quality_info = f"📐 **Resolution**: {img_width}x{img_height} ({megapixels:.1f}MP)"
            
            if uploaded_file == "camera_capture" and st.session_state.camera_info:
                camera_info = st.session_state.camera_info
                quality_info += f"\n📷 **Camera**: {camera_info.get('name', 'Unknown')}"
                
                # Quality recommendations
                if megapixels >= 8:
                    st.success(f"✅ Excellent quality! {quality_info}")
                elif megapixels >= 4:
                    st.info(f"👍 Good quality. {quality_info}")
                else:
                    st.warning(f"⚠️ Lower quality detected. Consider using a higher resolution camera. {quality_info}")
            else:
                st.info(quality_info)
        
        # Analysis button with dynamic text based on selected AI
        analysis_button_text = {
            'Basic Computer Vision': '🔍 Analyze Wall Defects (Basic)',
            'OpenAI GPT-4V': '🤖 Analyze with GPT-4V (Professional)',
            'Google Gemini Pro Vision': '🔮 Analyze with Gemini Pro Vision'
        }
        
        button_text = analysis_button_text.get(st.session_state.ai_analysis_mode, '🔍 Analyze Wall Defects')
        
        if st.button(button_text, key="analyze_btn"):
            # Check if AI provider is properly configured
            can_analyze = True
            error_message = ""
            
            if st.session_state.ai_analysis_mode == "OpenAI GPT-4V" and not st.session_state.openai_api_key:
                can_analyze = False
                error_message = "Please configure your OpenAI API key in the AI Analysis Settings above."
            elif st.session_state.ai_analysis_mode == "Google Gemini Pro Vision" and not st.session_state.gemini_api_key:
                can_analyze = False
                error_message = "Please configure your Gemini API key in the AI Analysis Settings above."
            
            if not can_analyze:
                st.error(f"❌ {error_message}")
            else:
                with st.spinner(f"Analyzing image with {st.session_state.ai_analysis_mode}..."):
                    # Perform basic computer vision analysis first
                    crack_results, nail_pop_results, color_results = analyze_wall_image(image)
                    
                    # Create basic analysis summary
                    basic_analysis = {
                        'cracks': crack_results['count'],
                        'crack_severity': crack_results['severity'],
                        'crack_length': crack_results['total_length'],
                        'nail_pops': nail_pop_results['count'],
                        'nail_pop_severity': nail_pop_results['severity'],
                        'water_damage_pixels': color_results['water_damage_pixels'],
                        'color_inconsistency_pixels': color_results['color_inconsistency_pixels'],
                        'color_severity': color_results['severity']
                    }
                    
                    # Enhanced AI analysis if selected
                    ai_analysis = None
                    if st.session_state.ai_analysis_mode != "Basic Computer Vision":
                        try:
                            # Get available AI providers
                            providers = get_available_providers(
                                openai_key=st.session_state.openai_api_key,
                                gemini_key=st.session_state.gemini_api_key
                            )
                            
                            # Select the appropriate provider
                            if st.session_state.ai_analysis_mode == "OpenAI GPT-4V" and "OpenAI GPT-4V" in providers:
                                ai_analysis = analyze_with_ai(providers["OpenAI GPT-4V"], image, basic_analysis)
                            elif st.session_state.ai_analysis_mode == "Google Gemini Pro Vision" and "Google Gemini Pro Vision" in providers:
                                ai_analysis = analyze_with_ai(providers["Google Gemini Pro Vision"], image, basic_analysis)
                                
                        except Exception as e:
                            st.error(f"AI analysis failed: {str(e)}")
                            ai_analysis = None
                    
                    # Create annotated image
                    annotated_image = create_comprehensive_annotation(
                        image, crack_results, nail_pop_results, color_results
                    )
                    
                    # Store results in session state
                    st.session_state.analysis_complete = True
                    st.session_state.detected_issues = basic_analysis
                    st.session_state.ai_analysis = ai_analysis
                    st.session_state.annotated_image = annotated_image
                    st.session_state.crack_results = crack_results
                    st.session_state.nail_pop_results = nail_pop_results
                    st.session_state.color_results = color_results
        
        # Display results if analysis is complete
        if st.session_state.analysis_complete:
            with col2:
                st.markdown("#### Detected Issues")
                st.image(st.session_state.annotated_image, use_container_width=True)
            
            # Results summary
            st.markdown("### 📊 Analysis Results")
            
            issues = st.session_state.detected_issues
            
            # Main metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Cracks Found", 
                    issues['cracks'],
                    help=f"Severity: {issues['crack_severity']}"
                )
            
            with col2:
                st.metric(
                    "Nail Pops", 
                    issues['nail_pops'],
                    help=f"Severity: {issues['nail_pop_severity']}"
                )
            
            with col3:
                st.metric(
                    "Water Damage", 
                    f"{issues['water_damage_pixels']:,} px",
                    help="Dark areas that may indicate water damage"
                )
            
            with col4:
                st.metric(
                    "Color Issues", 
                    f"{issues['color_inconsistency_pixels']:,} px",
                    help=f"Severity: {issues['color_severity']}"
                )
            
            # Detailed analysis
            if issues['cracks'] > 0:
                st.info(f"🔍 **Crack Analysis**: {issues['cracks']} cracks detected with total length of {issues['crack_length']:.1f} pixels. Severity: **{issues['crack_severity']}**")
            
            if issues['nail_pops'] > 0:
                st.info(f"🔍 **Nail Pop Analysis**: {issues['nail_pops']} potential nail pops detected. Severity: **{issues['nail_pop_severity']}**")
            
            if issues['water_damage_pixels'] > 1000:
                st.warning(f"💧 **Water Damage Alert**: {issues['water_damage_pixels']:,} pixels show signs of potential water damage")
            
            if issues['color_inconsistency_pixels'] > 2000:
                st.warning(f"🎨 **Color Inconsistency Alert**: {issues['color_inconsistency_pixels']:,} pixels show color variations")
            
            # AI Analysis Results (if available)
            if hasattr(st.session_state, 'ai_analysis') and st.session_state.ai_analysis:
                ai_result = st.session_state.ai_analysis
                
                if ai_result.get('success', False):
                    st.markdown("### 🤖 Professional AI Analysis")
                    st.success(f"✅ Analysis completed by {ai_result.get('provider', 'AI Model')}")
                    
                    # Overall condition
                    if 'overall_condition' in ai_result:
                        condition = ai_result['overall_condition']
                        condition_colors = {
                            'Good': '🟢',
                            'Fair': '🟡', 
                            'Poor': '🔴',
                            'Analyzed': '🔵'
                        }
                        color_icon = condition_colors.get(condition, '🔵')
                        st.markdown(f"**Overall Wall Condition**: {color_icon} {condition}")
                    
                    # Professional notes
                    if 'professional_notes' in ai_result:
                        with st.expander("📋 Professional Assessment", expanded=True):
                            st.markdown(ai_result['professional_notes'])
                    
                    # Detailed issues (if structured)
                    if 'detected_issues' in ai_result and ai_result['detected_issues']:
                        st.markdown("#### 🔍 Detailed Issue Analysis")
                        for i, issue in enumerate(ai_result['detected_issues']):
                            with st.expander(f"Issue {i+1}: {issue.get('type', 'Unknown').title()}", expanded=False):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown(f"**Severity**: {issue.get('severity', 'Unknown')}")
                                    st.markdown(f"**Location**: {issue.get('location', 'Not specified')}")
                                    st.markdown(f"**Priority**: {issue.get('priority', 'Medium')}")
                                
                                with col2:
                                    if 'estimated_cost' in issue:
                                        st.markdown(f"**Estimated Cost**: {issue['estimated_cost']}")
                                
                                if 'likely_cause' in issue:
                                    st.markdown(f"**Likely Cause**: {issue['likely_cause']}")
                                
                                if 'repair_method' in issue:
                                    st.markdown(f"**Repair Method**: {issue['repair_method']}")
                    
                    # Immediate actions
                    if 'immediate_actions' in ai_result and ai_result['immediate_actions']:
                        st.markdown("#### ⚡ Immediate Actions Required")
                        for action in ai_result['immediate_actions']:
                            st.warning(f"🚨 {action}")
                
                else:
                    # AI analysis failed
                    st.error(f"❌ AI Analysis Failed: {ai_result.get('error', 'Unknown error')}")
                    st.info("💡 Falling back to basic computer vision analysis results above.")
            
            # Legend
            st.markdown("### 🎨 Detection Legend")
            legend_col1, legend_col2 = st.columns(2)
            
            with legend_col1:
                st.markdown("""
                - 🔴 **Red lines**: Detected cracks
                - 🔵 **Blue areas**: Potential water damage
                """)
            
            with legend_col2:
                st.markdown("""
                - 🟡 **Yellow areas**: Color inconsistencies
                - 🟢 **Green circles**: Potential nail pops
                """)
            
            # Image naming and saving section
            st.markdown("### 📝 Save & Share Results")
            
            wall_name = st.text_input(
                "Name this wall inspection:",
                placeholder="e.g., Kitchen East Wall",
                key="wall_name"
            )
            
            if wall_name:
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("💾 Save & Generate Share Link", key="save_btn"):
                        with st.spinner("Saving to cloud storage..."):
                            # Try Google Drive first
                            drive_service = get_drive_service()
                            
                            # Initialize Google Drive service
                            drive_initialized = (
                                drive_service.initialize_from_secrets() or 
                                drive_service.initialize_from_file("credentials.json")
                            )
                            
                            if drive_initialized:
                                # Prepare images
                                original_img_buffer = io.BytesIO()
                                image.save(original_img_buffer, format='PNG')
                                original_img_bytes = original_img_buffer.getvalue()
                                
                                annotated_img_buffer = io.BytesIO()
                                annotated_pil = Image.fromarray(st.session_state.annotated_image)
                                annotated_pil.save(annotated_img_buffer, format='PNG')
                                annotated_img_bytes = annotated_img_buffer.getvalue()
                                
                                # Generate comprehensive report
                                report = {
                                    "wall_name": wall_name,
                                    "analysis_date": datetime.now().isoformat(),
                                    "analysis_method": st.session_state.ai_analysis_mode,
                                    "detected_issues": issues,
                                    "recommendations": generate_recommendations(issues)
                                }
                                
                                # Add AI analysis if available
                                if hasattr(st.session_state, 'ai_analysis') and st.session_state.ai_analysis:
                                    report["ai_analysis"] = st.session_state.ai_analysis
                                
                                # Upload to Google Drive
                                folder_link = drive_service.upload_inspection_results(
                                    wall_name, original_img_bytes, annotated_img_bytes, report
                                )
                                
                                if folder_link:
                                    st.success("✅ Analysis uploaded to Google Drive!")
                                    st.markdown(f"**Share this link with your contractor:**")
                                    st.code(folder_link, language=None)
                                    st.markdown(f"[📁 Open in Google Drive]({folder_link})")
                                else:
                                    st.error("Failed to upload to Google Drive. Using local download instead.")
                                    drive_initialized = False
                            
                            # Fallback to local download
                            if not drive_initialized:
                                st.info("📱 Google Drive not configured. Using local download.")
                
                with col2:
                    if st.button("📥 Download Files", key="download_btn"):
                        # Convert annotated image to bytes for download
                        img_buffer = io.BytesIO()
                        annotated_pil = Image.fromarray(st.session_state.annotated_image)
                        annotated_pil.save(img_buffer, format='PNG')
                        img_buffer.seek(0)
                        
                        # Create download button
                        st.download_button(
                            label="📥 Download Annotated Image",
                            data=img_buffer.getvalue(),
                            file_name=f"{wall_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                            mime="image/png"
                        )
                        
                        # Generate comprehensive report
                        report = {
                            "wall_name": wall_name,
                            "analysis_date": datetime.now().isoformat(),
                            "analysis_method": st.session_state.ai_analysis_mode,
                            "detected_issues": issues,
                            "recommendations": generate_recommendations(issues)
                        }
                        
                        # Add AI analysis if available
                        if hasattr(st.session_state, 'ai_analysis') and st.session_state.ai_analysis:
                            report["ai_analysis"] = st.session_state.ai_analysis
                        
                        report_json = json.dumps(report, indent=2)
                        
                        st.download_button(
                            label="📄 Download Analysis Report",
                            data=report_json,
                            file_name=f"{wall_name.replace(' ', '_')}_report.json",
                            mime="application/json"
                        )
                
                # Google Drive setup instructions
                if not is_drive_available():
                    with st.expander("🔧 Setup Google Drive Sharing (Optional)"):
                        st.markdown("""
                        To enable Google Drive sharing:
                        
                        1. **Create a Google Cloud Project**:
                           - Go to [Google Cloud Console](https://console.cloud.google.com/)
                           - Create a new project or select existing one
                        
                        2. **Enable Google Drive API**:
                           - Navigate to "APIs & Services" > "Library"
                           - Search for "Google Drive API" and enable it
                        
                        3. **Create Service Account**:
                           - Go to "APIs & Services" > "Credentials"
                           - Click "Create Credentials" > "Service Account"
                           - Download the JSON key file
                        
                        4. **Configure Streamlit Secrets**:
                           - Add the service account JSON content to `.streamlit/secrets.toml`
                           - Or place the JSON file as `credentials.json` in the project root
                        
                        5. **Share Drive Folder**:
                           - Create a folder in Google Drive
                           - Share it with the service account email
                        """)
                
                st.success("✅ Analysis complete! Files ready for sharing with contractors.")

def generate_recommendations(issues):
    """Generate recommendations based on detected issues"""
    recommendations = []
    
    # Crack recommendations
    if issues['cracks'] > 0:
        if issues['crack_severity'] == 'Severe':
            recommendations.append("🔴 URGENT: Severe cracks detected - Professional inspection recommended")
        elif issues['crack_severity'] == 'Moderate':
            recommendations.append("🟡 Moderate cracks found - Fill with mesh tape and compound, then sand and paint")
        else:
            recommendations.append("🟢 Minor cracks detected - Apply spackling compound and touch-up paint")
    
    # Water damage recommendations
    if issues['water_damage_pixels'] > 2000:
        recommendations.append("💧 Significant water damage signs - Check for leaks, dry thoroughly, treat with primer")
    elif issues['water_damage_pixels'] > 500:
        recommendations.append("💧 Potential water damage - Investigate moisture source and monitor")
    
    # Color inconsistency recommendations
    if issues['color_inconsistency_pixels'] > 3000:
        if issues['color_severity'] == 'Severe':
            recommendations.append("🎨 Major color inconsistencies - Full wall repainting recommended")
        else:
            recommendations.append("🎨 Color variations detected - Touch-up painting or spot treatment needed")
    
    # Nail pop recommendations
    if issues['nail_pops'] > 0:
        if issues['nail_pop_severity'] == 'Severe':
            recommendations.append("🔨 Multiple nail pops found - Check for structural movement, re-secure drywall")
        elif issues['nail_pop_severity'] == 'Moderate':
            recommendations.append("🔨 Several nail pops detected - Sand, fill with compound, prime and paint")
        else:
            recommendations.append("🔨 Minor nail pops found - Fill with spackling compound and touch-up paint")
    
    # Overall assessment
    total_issues = sum([
        1 if issues['cracks'] > 0 else 0,
        1 if issues['nail_pops'] > 0 else 0,
        1 if issues['water_damage_pixels'] > 500 else 0,
        1 if issues['color_inconsistency_pixels'] > 1000 else 0
    ])
    
    if total_issues == 0:
        recommendations.append("✅ No significant issues detected - Wall appears to be in good condition")
    elif total_issues >= 3:
        recommendations.append("⚠️ Multiple issues detected - Consider professional assessment")
    
    return recommendations

if __name__ == "__main__":
    main()
