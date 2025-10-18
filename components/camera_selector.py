"""
Custom camera selector component for Streamlit
Allows users to choose between multiple cameras (front/back, integrated/external)
"""

import streamlit as st
import streamlit.components.v1 as components
import base64
from PIL import Image
import io

def camera_selector():
    """
    Render a camera selector component with device enumeration
    Returns the captured image as a PIL Image object
    """
    
    # HTML/JavaScript for camera selection and capture
    camera_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            .camera-container {
                max-width: 100%;
                margin: 0 auto;
                padding: 20px;
                text-align: center;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                min-height: 600px;
                display: flex;
                flex-direction: column;
            }
            
            .button-section {
                margin-top: auto;
                padding: 20px;
                border-top: 2px solid #e0e0e0;
                background: rgba(255, 255, 255, 0.9);
                border-radius: 0 0 15px 15px;
                margin: 20px -20px -20px -20px;
            }
            
            .camera-controls {
                margin: 20px 0;
                display: flex;
                flex-direction: column;
                gap: 15px;
                align-items: center;
            }
            
            .camera-select {
                padding: 12px 20px;
                font-size: 16px;
                border: 2px solid #667eea;
                border-radius: 8px;
                background: white;
                color: #333;
                min-width: 250px;
                cursor: pointer;
            }
            
            .camera-select:focus {
                outline: none;
                border-color: #FF6B6B;
                box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.1);
            }
            
            video {
                max-width: 100%;
                max-height: 300px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                background: #000;
                margin-bottom: 15px;
            }
            
            .capture-btn {
                background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 18px;
                font-weight: 600;
                border-radius: 50px;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
                transition: all 0.3s ease;
                margin: 10px 5px;
                min-width: 180px;
                display: inline-block;
            }
            
            .capture-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
            }
            
            .capture-btn:disabled {
                background: #ccc !important;
                cursor: not-allowed !important;
                transform: none !important;
                box-shadow: none !important;
                opacity: 0.5 !important;
            }
            
            .capture-btn:not(:disabled) {
                opacity: 1 !important;
            }
            
            .switch-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 600;
                border-radius: 25px;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                transition: all 0.3s ease;
                margin: 10px;
            }
            
            .switch-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            }
            
            .error-message {
                color: #e74c3c;
                background: #fdf2f2;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #e74c3c;
                margin: 15px 0;
                font-weight: 500;
            }
            
            .info-message {
                color: #3498db;
                background: #f0f8ff;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #3498db;
                margin: 15px 0;
            }
            
            .camera-info {
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
                border: 1px solid #e0e0e0;
                text-align: left;
            }
            
            .mobile-controls {
                display: none;
            }
            
            @media (max-width: 768px) {
                .camera-container {
                    padding: 15px;
                }
                
                .camera-select {
                    min-width: 100%;
                    font-size: 18px;
                    padding: 15px;
                }
                
                .capture-btn {
                    width: 100%;
                    max-width: 300px;
                    padding: 18px;
                    font-size: 20px;
                }
                
                .switch-btn {
                    width: 100%;
                    max-width: 200px;
                    padding: 15px;
                    font-size: 18px;
                }
                
                .mobile-controls {
                    display: block;
                }
                
                video {
                    max-height: 250px;
                }
                
                .button-section {
                    position: sticky;
                    bottom: 0;
                    z-index: 100;
                }
            }
        </style>
    </head>
    <body>
        <div class="camera-container">
            <h3>📸 Select Camera</h3>
            
            <div class="camera-controls">
                <select id="cameraSelect" class="camera-select">
                    <option value="">🔍 Detecting cameras...</option>
                </select>
                
                <div class="mobile-controls">
                    <button id="switchCamera" class="switch-btn">🔄 Switch Camera</button>
                </div>
            </div>
            
            <div id="cameraInfo" class="camera-info" style="display: none;">
                <strong>Current Camera:</strong> <span id="currentCameraName">Unknown</span><br>
                <strong>Resolution:</strong> <span id="currentResolution">Unknown</span><br>
                <strong>Facing:</strong> <span id="currentFacing">Unknown</span>
            </div>
            
            <div id="errorMessage" class="error-message" style="display: none;"></div>
            <div id="infoMessage" class="info-message" style="display: none;"></div>
            
            <video id="video" autoplay playsinline muted style="display: none;"></video>
            <canvas id="canvas" style="display: none;"></canvas>
            
            <div class="button-section">
                <button id="startCamera" class="capture-btn">📷 Start Camera</button>
                <button id="captureBtn" class="capture-btn" disabled style="opacity: 0.5;">📸 Capture Photo</button>
                <button id="retakeBtn" class="capture-btn" style="display: none;">🔄 Retake</button>
            </div>
        </div>

        <script>
            let videoStream = null;
            let cameras = [];
            let currentCameraIndex = 0;
            let isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            
            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            const cameraSelect = document.getElementById('cameraSelect');
            const startCameraBtn = document.getElementById('startCamera');
            const captureBtn = document.getElementById('captureBtn');
            const retakeBtn = document.getElementById('retakeBtn');
            const switchCameraBtn = document.getElementById('switchCamera');
            const errorMessage = document.getElementById('errorMessage');
            const infoMessage = document.getElementById('infoMessage');
            const cameraInfo = document.getElementById('cameraInfo');
            const currentCameraName = document.getElementById('currentCameraName');
            const currentResolution = document.getElementById('currentResolution');
            const currentFacing = document.getElementById('currentFacing');
            
            // Show info message
            function showInfo(message) {
                infoMessage.textContent = message;
                infoMessage.style.display = 'block';
                errorMessage.style.display = 'none';
            }
            
            // Show error message
            function showError(message) {
                errorMessage.textContent = message;
                errorMessage.style.display = 'block';
                infoMessage.style.display = 'none';
            }
            
            // Hide messages
            function hideMessages() {
                errorMessage.style.display = 'none';
                infoMessage.style.display = 'none';
            }
            
            // Get camera label with enhanced detection
            function getCameraLabel(device) {
                let label = device.label || `Camera ${cameras.indexOf(device) + 1}`;
                
                // Enhanced mobile camera detection
                if (isMobile) {
                    if (label.toLowerCase().includes('back') || label.toLowerCase().includes('rear')) {
                        return `📱 Back Camera (${label})`;
                    } else if (label.toLowerCase().includes('front') || label.toLowerCase().includes('user')) {
                        return `🤳 Front Camera (${label})`;
                    } else if (device.getCapabilities) {
                        const capabilities = device.getCapabilities();
                        if (capabilities.facingMode) {
                            if (capabilities.facingMode.includes('environment')) {
                                return `📱 Back Camera (${label})`;
                            } else if (capabilities.facingMode.includes('user')) {
                                return `🤳 Front Camera (${label})`;
                            }
                        }
                    }
                }
                
                // Desktop camera detection
                if (label.toLowerCase().includes('integrated') || label.toLowerCase().includes('built-in')) {
                    return `💻 Built-in Camera (${label})`;
                } else if (label.toLowerCase().includes('usb') || label.toLowerCase().includes('external')) {
                    return `📹 External Camera (${label})`;
                } else if (label.toLowerCase().includes('webcam')) {
                    return `🎥 Webcam (${label})`;
                }
                
                return `📷 ${label}`;
            }
            
            // Enumerate cameras
            async function enumerateCameras() {
                try {
                    showInfo('🔍 Detecting available cameras...');
                    
                    // Request permissions first
                    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                    stream.getTracks().forEach(track => track.stop());
                    
                    const devices = await navigator.mediaDevices.enumerateDevices();
                    cameras = devices.filter(device => device.kind === 'videoinput');
                    
                    if (cameras.length === 0) {
                        showError('❌ No cameras found. Please check camera permissions.');
                        return;
                    }
                    
                    // Populate camera select
                    cameraSelect.innerHTML = '';
                    cameras.forEach((camera, index) => {
                        const option = document.createElement('option');
                        option.value = camera.deviceId;
                        option.textContent = getCameraLabel(camera);
                        cameraSelect.appendChild(option);
                    });
                    
                    // Set default camera (prefer back camera on mobile)
                    let defaultCamera = null;
                    if (isMobile) {
                        defaultCamera = cameras.find(camera => 
                            camera.label.toLowerCase().includes('back') || 
                            camera.label.toLowerCase().includes('rear') ||
                            camera.label.toLowerCase().includes('environment')
                        );
                        if (defaultCamera) {
                            cameraSelect.value = defaultCamera.deviceId;
                            currentCameraIndex = cameras.indexOf(defaultCamera);
                        }
                    }
                    
                    if (!defaultCamera && cameras.length > 0) {
                        cameraSelect.value = cameras[0].deviceId;
                        defaultCamera = cameras[0];
                    }
                    
                    showInfo(`✅ Found ${cameras.length} camera(s). Select a camera and click "Start Camera" to begin. ${isMobile ? 'Back camera recommended for better quality.' : 'External cameras typically offer better quality.'}`);
                    
                    // Auto-start the default camera
                    if (defaultCamera) {
                        setTimeout(() => {
                            startCamera(defaultCamera.deviceId);
                        }, 1000);
                    }
                    
                } catch (error) {
                    console.error('Error enumerating cameras:', error);
                    showError('❌ Unable to access cameras. Please allow camera permissions and try again.');
                }
            }
            
            // Start camera with selected device
            async function startCamera(deviceId = null) {
                try {
                    if (videoStream) {
                        videoStream.getTracks().forEach(track => track.stop());
                    }
                    
                    const constraints = {
                        video: {
                            deviceId: deviceId ? { exact: deviceId } : undefined,
                            width: { ideal: 1920, max: 4096 },
                            height: { ideal: 1080, max: 2160 },
                            facingMode: isMobile && !deviceId ? { ideal: 'environment' } : undefined
                        }
                    };
                    
                    showInfo('📷 Starting camera...');
                    
                    videoStream = await navigator.mediaDevices.getUserMedia(constraints);
                    video.srcObject = videoStream;
                    video.style.display = 'block';
                    
                    // Update camera info
                    const track = videoStream.getVideoTracks()[0];
                    const settings = track.getSettings();
                    const capabilities = track.getCapabilities();
                    
                    currentCameraName.textContent = track.label || 'Unknown Camera';
                    currentResolution.textContent = `${settings.width}x${settings.height}`;
                    currentFacing.textContent = settings.facingMode || 'Unknown';
                    cameraInfo.style.display = 'block';
                    
                    captureBtn.disabled = false;
                    captureBtn.style.display = 'inline-block';
                    captureBtn.style.opacity = '1';
                    startCameraBtn.style.display = 'none';
                    
                    // Show success message with capture instruction
                    showInfo('📷 Camera ready! Click "Capture Photo" button below to take a picture.');
                    setTimeout(hideMessages, 3000);
                    
                } catch (error) {
                    console.error('Error starting camera:', error);
                    showError(`❌ Failed to start camera: ${error.message}`);
                }
            }
            
            // Switch to next camera (mobile)
            function switchCamera() {
                if (cameras.length <= 1) return;
                
                currentCameraIndex = (currentCameraIndex + 1) % cameras.length;
                const selectedCamera = cameras[currentCameraIndex];
                cameraSelect.value = selectedCamera.deviceId;
                startCamera(selectedCamera.deviceId);
            }
            
            // Capture photo
            function capturePhoto() {
                const context = canvas.getContext('2d');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                context.drawImage(video, 0, 0);
                
                // Convert to base64
                const imageData = canvas.toDataURL('image/png');
                
                // Send to Streamlit
                const captureData = {
                    image: imageData,
                    camera: {
                        name: currentCameraName.textContent,
                        resolution: currentResolution.textContent,
                        facing: currentFacing.textContent
                    }
                };
                
                // Send via Streamlit component API
                window.parent.postMessage({
                    type: 'streamlit:componentValue',
                    value: captureData
                }, '*');
                
                // Show retake button
                captureBtn.style.display = 'none';
                retakeBtn.style.display = 'inline-block';
                video.style.display = 'none';
            }
            
            // Retake photo
            function retakePhoto() {
                captureBtn.style.display = 'inline-block';
                retakeBtn.style.display = 'none';
                video.style.display = 'block';
            }
            
            // Event listeners
            startCameraBtn.addEventListener('click', () => {
                const selectedDeviceId = cameraSelect.value;
                startCamera(selectedDeviceId || null);
            });
            
            cameraSelect.addEventListener('change', (e) => {
                if (e.target.value) {
                    startCamera(e.target.value);
                }
            });
            
            switchCameraBtn.addEventListener('click', switchCamera);
            captureBtn.addEventListener('click', capturePhoto);
            retakeBtn.addEventListener('click', retakePhoto);
            
            // Initialize
            enumerateCameras();
            
            // Show mobile controls on mobile devices
            if (isMobile) {
                document.querySelector('.mobile-controls').style.display = 'block';
            }
        </script>
    </body>
    </html>
    """
    
    # Render the component with increased height to ensure buttons are visible
    result = components.html(camera_html, height=700, scrolling=True)
    
    return result

def process_camera_result(camera_data):
    """
    Process the camera result from the JavaScript component
    Returns PIL Image object
    """
    # Check if camera_data is valid and is a dictionary
    if camera_data and isinstance(camera_data, dict) and 'image' in camera_data:
        try:
            # Remove data URL prefix
            image_data = camera_data['image'].split(',')[1]
            
            # Decode base64 to image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            return image, camera_data.get('camera', {})
        except Exception as e:
            st.error(f"Error processing camera image: {str(e)}")
            return None, None
    
    return None, None

