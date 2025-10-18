"""
Wall Inspector - AI-powered wall damage detection web app
Mobile-Optimized Version with Step Wizard Interface
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
    layout="centered",  # Changed from wide to centered for better mobile experience
    initial_sidebar_state="collapsed"
)

# Enhanced Mobile CSS with Wizard Interface
st.markdown("""
<style>
    /* Remove default padding */
    .main > div {
        padding-top: 0rem;
        padding-bottom: 80px; /* Space for sticky bottom bar */
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }

    /* Progress bar styling */
    .progress-container {
        position: sticky;
        top: 0;
        z-index: 999;
        background: white;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: -1rem -1rem 1rem -1rem;
    }

    .progress-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    .progress-step {
        flex: 1;
        text-align: center;
        padding: 0.5rem;
        font-size: 0.85rem;
        color: #999;
        position: relative;
    }

    .progress-step.active {
        color: #667eea;
        font-weight: 600;
    }

    .progress-step.completed {
        color: #4CAF50;
    }

    .progress-step::after {
        content: '';
        position: absolute;
        top: 50%;
        right: -50%;
        width: 100%;
        height: 2px;
        background: #e0e0e0;
        z-index: -1;
    }

    .progress-step:last-child::after {
        display: none;
    }

    .progress-step.completed::after {
        background: #4CAF50;
    }

    /* Sticky bottom action bar */
    .bottom-action-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 1rem;
        box-shadow: 0 -4px 15px rgba(0,0,0,0.1);
        z-index: 1000;
        display: flex;
        gap: 0.5rem;
        justify-content: space-between;
    }

    .bottom-action-bar button {
        flex: 1;
        height: 3.5rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 12px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .btn-back {
        background: #f0f0f0;
        color: #333;
    }

    .btn-next {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    .btn-analyze {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #f8f9fa;
        border-radius: 12px;
        padding: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        color: #666;
        font-weight: 500;
        padding: 0 1rem;
    }

    .stTabs [aria-selected="true"] {
        background: white;
        color: #667eea;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* Button styling */
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

    /* Compact card styling */
    .compact-card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin: 1rem 0;
    }

    /* Image containers - smaller on mobile */
    .stImage > img {
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        max-height: 400px;
        object-fit: contain;
    }

    /* Compact metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
    }

    /* Hide expander arrows by default on mobile */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }

        /* Make images more compact */
        .stImage > img {
            max-height: 300px;
        }

        /* Smaller metrics on mobile */
        [data-testid="stMetricValue"] {
            font-size: 1.2rem;
        }

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        header {visibility: hidden;}
    }

    /* App header */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 1rem;
        border-radius: 0;
        margin: -1rem -1rem 1rem -1rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    .app-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }

    .app-header p {
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
        opacity: 0.9;
    }

    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }

    .status-ready {
        background: #4CAF50;
        color: white;
    }

    .status-pending {
        background: #FFC107;
        color: #333;
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
    try:
        models = load_detection_models()

        # Start with original image
        annotated = np.array(image).copy()

        # Add color overlays first (as background) - with error handling
        try:
            annotated = models['color_analyzer'].create_color_overlay(annotated, color_results)
        except Exception as e:
            print(f"Warning: Color overlay failed: {e}")

        # Add crack annotations - with error handling
        try:
            annotated = models['crack_detector'].draw_cracks(annotated, crack_results)
        except Exception as e:
            print(f"Warning: Crack annotation failed: {e}")

        # Add nail pop annotations - with error handling
        try:
            annotated = models['nail_pop_detector'].draw_nail_pops(annotated, nail_pop_results)
        except Exception as e:
            print(f"Warning: Nail pop annotation failed: {e}")

        return annotated

    except Exception as e:
        # If all annotation fails, return original image
        print(f"Error: Annotation creation failed: {e}")
        return np.array(image)

def render_progress_bar(current_step, steps):
    """Render progress indicator"""
    progress_html = '<div class="progress-container"><div class="progress-bar">'

    for i, step in enumerate(steps):
        status_class = ""
        if i < current_step:
            status_class = "completed"
        elif i == current_step:
            status_class = "active"

        progress_html += f'<div class="progress-step {status_class}">{step}</div>'

    progress_html += '</div></div>'
    st.markdown(progress_html, unsafe_allow_html=True)

def convert_to_serializable(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

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

def main():
    # App header
    st.markdown("""
    <div class="app-header">
        <h1>🏠 Wall Inspector</h1>
        <p>AI-powered damage detection made simple</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state for wizard
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'detected_issues' not in st.session_state:
        st.session_state.detected_issues = []
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

    # Define wizard steps
    steps = ["📸 Capture", "⚙️ Settings", "🔍 Analyze", "📊 Results"]

    # Render progress bar
    render_progress_bar(st.session_state.current_step, steps)

    # STEP 0: Image Capture
    if st.session_state.current_step == 0:
        st.markdown("### 📸 Step 1: Capture Wall Image")
        st.info("💡 Use your back camera for best quality on mobile devices")

        # Camera mode selection - simplified
        camera_mode = st.radio(
            "Choose capture method:",
            ["📱 Simple Camera", "📁 Upload from Gallery"],
            key="camera_mode_radio",
            label_visibility="collapsed"
        )

        uploaded_file = None

        if camera_mode == "📱 Simple Camera":
            uploaded_file = st.camera_input("Take a picture of the wall", key="simple_camera")
        else:
            uploaded_file = st.file_uploader(
                "Choose an image from your device",
                type=['png', 'jpg', 'jpeg', 'webp'],
                key="file_upload",
                help="Supported formats: PNG, JPG, JPEG, WebP"
            )

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.session_state.captured_image = image

            # Show preview
            st.markdown("#### Preview")
            st.image(image, use_container_width=True)

            # Show quality info
            img_width, img_height = image.size
            megapixels = (img_width * img_height) / 1_000_000

            if megapixels >= 8:
                st.success(f"✅ Excellent quality: {img_width}x{img_height} ({megapixels:.1f}MP)")
            elif megapixels >= 4:
                st.info(f"👍 Good quality: {img_width}x{img_height} ({megapixels:.1f}MP)")
            else:
                st.warning(f"⚠️ Lower quality: {img_width}x{img_height} ({megapixels:.1f}MP)")

            # Show next button
            col1, col2 = st.columns(2)
            with col2:
                if st.button("Next: Settings →", key="step0_next", use_container_width=True):
                    st.session_state.current_step = 1
                    st.rerun()

        # Tips
        with st.expander("📖 Tips for Best Results"):
            st.markdown("""
            - **Lighting**: Use natural light when possible
            - **Distance**: Get close enough to see wall texture
            - **Stability**: Hold device steady or use a tripod
            - **Angle**: Take photo straight-on, not at an angle
            - **Quality**: Higher resolution = better detection
            """)

    # STEP 1: Settings
    elif st.session_state.current_step == 1:
        st.markdown("### ⚙️ Step 2: Analysis Settings (Optional)")
        st.info("💡 Skip this step to use free basic analysis")

        # AI Analysis Configuration
        analysis_mode = st.radio(
            "Choose analysis method:",
            [
                "🔧 Basic (Free)",
                "🤖 AI Professional (Paid)"
            ],
            key="analysis_mode_simple"
        )

        if analysis_mode == "🤖 AI Professional (Paid)":
            ai_provider = st.selectbox(
                "Select AI Provider:",
                ["OpenAI GPT-4V", "Google Gemini 2.5 Flash"]
            )

            if ai_provider == "OpenAI GPT-4V":
                st.session_state.ai_analysis_mode = "OpenAI GPT-4V"
                openai_key = st.text_input(
                    "OpenAI API Key:",
                    type="password",
                    value=st.session_state.openai_api_key,
                    placeholder="sk-...",
                    help="Get your API key from platform.openai.com"
                )
                st.session_state.openai_api_key = openai_key.strip() if openai_key else ""

                if openai_key:
                    st.success("✅ API key configured")
            else:
                st.session_state.ai_analysis_mode = "Google Gemini"
                gemini_key = st.text_input(
                    "Gemini API Key:",
                    type="password",
                    value=st.session_state.gemini_api_key,
                    placeholder="AIza...",
                    help="Get your API key from aistudio.google.com"
                )
                st.session_state.gemini_api_key = gemini_key.strip().rstrip('\\') if gemini_key else ""

                if gemini_key:
                    st.success("✅ API key configured")
        else:
            st.session_state.ai_analysis_mode = "Basic Computer Vision"

        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", key="step1_back", use_container_width=True):
                st.session_state.current_step = 0
                st.rerun()
        with col2:
            if st.button("Next: Analyze →", key="step1_next", use_container_width=True):
                st.session_state.current_step = 2
                st.rerun()

    # STEP 2: Analysis
    elif st.session_state.current_step == 2:
        st.markdown("### 🔍 Step 3: Run Analysis")

        if st.session_state.captured_image is None:
            st.error("❌ No image captured. Please go back to Step 1.")
            if st.button("← Back to Capture", key="step2_back_error", use_container_width=True):
                st.session_state.current_step = 0
                st.rerun()
        else:
            # Show preview
            st.markdown("#### Image to Analyze")
            st.image(st.session_state.captured_image, use_container_width=True)

            # Show analysis mode
            mode_display = {
                'Basic Computer Vision': '🔧 Basic (Free)',
                'OpenAI GPT-4V': '🤖 AI Professional (OpenAI)',
                'Google Gemini': '🔮 AI Professional (Gemini)'
            }
            st.info(f"**Analysis Mode**: {mode_display.get(st.session_state.ai_analysis_mode, 'Basic')}")

            # Analyze button
            if st.button("🔍 Start Analysis", key="analyze_btn", use_container_width=True, type="primary"):
                # Check if AI provider is properly configured
                can_analyze = True
                error_message = ""

                if st.session_state.ai_analysis_mode == "OpenAI GPT-4V" and not st.session_state.openai_api_key:
                    can_analyze = False
                    error_message = "Please configure your OpenAI API key in Settings"
                elif st.session_state.ai_analysis_mode == "Google Gemini" and not st.session_state.gemini_api_key:
                    can_analyze = False
                    error_message = "Please configure your Gemini API key in Settings"

                if not can_analyze:
                    st.error(f"❌ {error_message}")
                else:
                    with st.spinner(f"Analyzing with {st.session_state.ai_analysis_mode}..."):
                        image = st.session_state.captured_image

                        # Perform basic computer vision analysis
                        try:
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
                            basic_analysis = {
                                'cracks': 0, 'crack_severity': 'None', 'crack_length': 0,
                                'nail_pops': 0, 'nail_pop_severity': 'None',
                                'water_damage_pixels': 0, 'color_inconsistency_pixels': 0,
                                'color_severity': 'None'
                            }
                            crack_results = {'count': 0, 'severity': 'None', 'total_length': 0, 'contours': []}
                            nail_pop_results = {'count': 0, 'severity': 'None', 'circles': []}
                            color_results = {'water_damage_pixels': 0, 'color_inconsistency_pixels': 0,
                                           'severity': 'None', 'dark_areas': None, 'unusual_saturation': None}

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
                                st.error(f"AI analysis failed: {str(e)}")

                        # Create annotated image
                        annotated_image = create_comprehensive_annotation(
                            image, crack_results, nail_pop_results, color_results
                        )

                        # Store results
                        st.session_state.analysis_complete = True
                        st.session_state.detected_issues = basic_analysis
                        st.session_state.ai_analysis = ai_analysis
                        st.session_state.annotated_image = annotated_image
                        st.session_state.crack_results = crack_results
                        st.session_state.nail_pop_results = nail_pop_results
                        st.session_state.color_results = color_results
                        st.session_state.current_step = 3
                        st.rerun()

            # Back button
            if st.button("← Back to Settings", key="step2_back", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()

    # STEP 3: Results
    elif st.session_state.current_step == 3:
        if not st.session_state.analysis_complete:
            st.error("❌ No analysis results. Please run analysis first.")
            if st.button("← Back to Analysis", key="step3_back_error", use_container_width=True):
                st.session_state.current_step = 2
                st.rerun()
        else:
            st.markdown("### 📊 Step 4: Analysis Results")

            # Use tabs for organized display
            tab1, tab2, tab3 = st.tabs(["📸 Images", "📈 Metrics", "💾 Save"])

            # TAB 1: Images
            with tab1:
                st.markdown("#### Before & After")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Original**")
                    st.image(st.session_state.captured_image, use_container_width=True)
                with col2:
                    st.markdown("**Detected**")
                    st.image(st.session_state.annotated_image, use_container_width=True)

                # Legend
                with st.expander("🎨 Detection Legend"):
                    st.markdown("""
                    - 🔴 **Red lines**: Cracks
                    - 🔵 **Blue areas**: Water damage
                    - 🟡 **Yellow areas**: Color issues
                    - 🟢 **Green circles**: Nail pops
                    """)

            # TAB 2: Metrics & Analysis
            with tab2:
                issues = st.session_state.detected_issues

                # Quick metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Cracks", issues['cracks'])
                    st.metric("Water Damage", f"{issues['water_damage_pixels']:,} px")
                with col2:
                    st.metric("Nail Pops", issues['nail_pops'])
                    st.metric("Color Issues", f"{issues['color_inconsistency_pixels']:,} px")

                # AI Analysis if available
                if hasattr(st.session_state, 'ai_analysis') and st.session_state.ai_analysis:
                    ai_result = st.session_state.ai_analysis

                    if ai_result.get('success', False):
                        st.success(f"✅ Professional analysis by {ai_result.get('provider', 'AI')}")

                        if 'overall_condition' in ai_result:
                            condition_colors = {'Good': '🟢', 'Fair': '🟡', 'Poor': '🔴', 'Analyzed': '🔵'}
                            color_icon = condition_colors.get(ai_result['overall_condition'], '🔵')
                            st.markdown(f"**Condition**: {color_icon} {ai_result['overall_condition']}")

                        if 'professional_notes' in ai_result:
                            with st.expander("📋 Professional Assessment", expanded=True):
                                st.markdown(ai_result['professional_notes'])

                # Recommendations
                st.markdown("#### 💡 Recommendations")
                recommendations = generate_recommendations(issues)
                for rec in recommendations:
                    st.info(rec)

            # TAB 3: Save & Share
            with tab3:
                wall_name = st.text_input(
                    "Name this inspection:",
                    placeholder="e.g., Kitchen East Wall",
                    key="wall_name"
                )

                if wall_name:
                    # Download button
                    img_buffer = io.BytesIO()
                    annotated_pil = Image.fromarray(st.session_state.annotated_image)
                    annotated_pil.save(img_buffer, format='PNG')
                    img_buffer.seek(0)

                    st.download_button(
                        label="📥 Download Annotated Image",
                        data=img_buffer.getvalue(),
                        file_name=f"{wall_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        mime="image/png",
                        use_container_width=True
                    )

                    # Report download
                    report = {
                        "wall_name": wall_name,
                        "analysis_date": datetime.now().isoformat(),
                        "analysis_method": st.session_state.ai_analysis_mode,
                        "detected_issues": convert_to_serializable(issues),
                        "recommendations": recommendations
                    }

                    if hasattr(st.session_state, 'ai_analysis') and st.session_state.ai_analysis:
                        report["ai_analysis"] = convert_to_serializable(st.session_state.ai_analysis)

                    report_json = json.dumps(report, indent=2)

                    st.download_button(
                        label="📄 Download Report (JSON)",
                        data=report_json,
                        file_name=f"{wall_name.replace(' ', '_')}_report.json",
                        mime="application/json",
                        use_container_width=True
                    )

                    st.success("✅ Ready to share with contractors!")
                else:
                    st.info("👆 Enter a name to enable downloads")

            # New analysis button
            st.markdown("---")
            if st.button("🔄 New Analysis", key="new_analysis", use_container_width=True):
                # Reset state
                st.session_state.current_step = 0
                st.session_state.analysis_complete = False
                st.session_state.captured_image = None
                st.session_state.detected_issues = []
                st.rerun()

if __name__ == "__main__":
    main()
