"""
Enhanced crack detection module using computer vision techniques
Based on research from open source crack detection projects
"""

import cv2
import numpy as np
from PIL import Image
import streamlit as st

class CrackDetector:
    def __init__(self):
        self.min_crack_area = 50
        self.min_aspect_ratio = 3
        self.canny_low = 50
        self.canny_high = 150
        self.gaussian_kernel = 5
        
    def preprocess_image(self, image):
        """Preprocess image for better crack detection"""
        # Convert PIL to numpy array
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (self.gaussian_kernel, self.gaussian_kernel), 0)
        
        # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(blurred)
        
        return enhanced
    
    def detect_edges(self, preprocessed_image):
        """Detect edges using Canny edge detector with adaptive thresholding"""
        # Calculate adaptive thresholds based on image statistics
        median = np.median(preprocessed_image)
        sigma = 0.33
        lower = int(max(0, (1.0 - sigma) * median))
        upper = int(min(255, (1.0 + sigma) * median))
        
        # Apply Canny edge detection
        edges = cv2.Canny(preprocessed_image, lower, upper)
        
        # Morphological operations to connect nearby edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        return edges
    
    def filter_crack_contours(self, contours):
        """Filter contours that are likely to be cracks"""
        crack_contours = []
        
        for contour in contours:
            # Calculate contour properties
            area = cv2.contourArea(contour)
            
            if area < self.min_crack_area:
                continue
            
            # Calculate bounding rectangle
            rect = cv2.minAreaRect(contour)
            width, height = rect[1]
            
            if width == 0 or height == 0:
                continue
            
            # Calculate aspect ratio
            aspect_ratio = max(width, height) / min(width, height)
            
            # Filter based on aspect ratio (cracks are typically long and thin)
            if aspect_ratio > self.min_aspect_ratio:
                # Additional filtering based on contour properties
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    # Compactness measure (4π*area/perimeter²)
                    compactness = 4 * np.pi * area / (perimeter * perimeter)
                    
                    # Cracks typically have low compactness
                    if compactness < 0.3:
                        crack_contours.append(contour)
        
        return crack_contours
    
    def detect_cracks(self, image):
        """Main crack detection function"""
        # Preprocess the image
        preprocessed = self.preprocess_image(image)
        
        # Detect edges
        edges = self.detect_edges(preprocessed)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours that are likely to be cracks
        crack_contours = self.filter_crack_contours(contours)
        
        # Calculate crack statistics
        total_crack_length = sum(cv2.arcLength(contour, False) for contour in crack_contours)
        
        return {
            'contours': crack_contours,
            'edges': edges,
            'count': len(crack_contours),
            'total_length': total_crack_length,
            'severity': self.assess_crack_severity(crack_contours)
        }
    
    def assess_crack_severity(self, crack_contours):
        """Assess crack severity based on detected contours"""
        if not crack_contours:
            return "None"
        
        max_area = max(cv2.contourArea(contour) for contour in crack_contours)
        total_length = sum(cv2.arcLength(contour, False) for contour in crack_contours)
        
        if max_area > 500 or total_length > 1000:
            return "Severe"
        elif max_area > 200 or total_length > 500:
            return "Moderate"
        else:
            return "Minor"
    
    def draw_cracks(self, image, crack_results, color=(255, 0, 0), thickness=2):
        """Draw detected cracks on the image"""
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        result_image = image.copy()
        
        if crack_results['contours']:
            cv2.drawContours(result_image, crack_results['contours'], -1, color, thickness)
        
        return result_image

class NailPopDetector:
    def __init__(self):
        self.min_radius = 3
        self.max_radius = 25
        self.min_dist = 20
        self.param1 = 50
        self.param2 = 30
    
    def detect_nail_pops(self, image):
        """Detect potential nail pops using improved circular detection"""
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Detect circles using HoughCircles
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=self.min_dist,
            param1=self.param1,
            param2=self.param2,
            minRadius=self.min_radius,
            maxRadius=self.max_radius
        )
        
        nail_pops = []
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for circle in circles[0, :]:
                x, y, r = circle
                # Additional validation: check if the area around the circle
                # has characteristics typical of nail pops
                if self.validate_nail_pop(gray, x, y, r):
                    nail_pops.append(circle)
        
        return {
            'circles': nail_pops,
            'count': len(nail_pops),
            'severity': self.assess_nail_pop_severity(nail_pops)
        }
    
    def validate_nail_pop(self, gray_image, x, y, radius):
        """Validate if detected circle is likely a nail pop"""
        # Check if coordinates are within image bounds
        h, w = gray_image.shape
        if x - radius < 0 or x + radius >= w or y - radius < 0 or y + radius >= h:
            return False
        
        # Extract region of interest
        roi = gray_image[y-radius:y+radius, x-radius:x+radius]
        
        if roi.size == 0:
            return False
        
        # Calculate variance in the circular region
        # Nail pops typically have higher variance due to shadows/highlights
        variance = np.var(roi)
        
        # Threshold based on typical nail pop characteristics
        return variance > 100  # Adjust threshold as needed
    
    def assess_nail_pop_severity(self, nail_pops):
        """Assess nail pop severity based on count and size"""
        if not nail_pops:
            return "None"
        
        count = len(nail_pops)
        avg_radius = np.mean([circle[2] for circle in nail_pops]) if nail_pops else 0
        
        if count > 10 or avg_radius > 15:
            return "Severe"
        elif count > 5 or avg_radius > 10:
            return "Moderate"
        else:
            return "Minor"
    
    def draw_nail_pops(self, image, nail_pop_results, color=(0, 255, 0), thickness=3):
        """Draw detected nail pops on the image"""
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        result_image = image.copy()
        
        for circle in nail_pop_results['circles']:
            x, y, r = circle
            cv2.circle(result_image, (x, y), r, color, thickness)
            cv2.circle(result_image, (x, y), 2, color, thickness)
        
        return result_image

class ColorAnalyzer:
    def __init__(self):
        self.water_damage_threshold = 1.5
        self.color_variance_threshold = 2.0
    
    def analyze_color_consistency(self, image):
        """Analyze color consistency and detect potential water damage"""
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Convert to different color spaces for analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        
        # Analyze brightness (V channel in HSV)
        brightness = hsv[:, :, 2]
        mean_brightness = np.mean(brightness)
        std_brightness = np.std(brightness)
        
        # Detect dark areas (potential water damage)
        dark_threshold = mean_brightness - self.water_damage_threshold * std_brightness
        dark_areas = brightness < dark_threshold
        
        # Analyze color saturation
        saturation = hsv[:, :, 1]
        mean_saturation = np.mean(saturation)
        std_saturation = np.std(saturation)
        
        # Detect areas with unusual saturation
        unusual_saturation = np.abs(saturation - mean_saturation) > self.color_variance_threshold * std_saturation
        
        # Analyze color uniformity using LAB color space
        l_channel = lab[:, :, 0]
        a_channel = lab[:, :, 1]
        b_channel = lab[:, :, 2]
        
        # Calculate color variance
        color_variance = np.var(l_channel) + np.var(a_channel) + np.var(b_channel)
        
        return {
            'dark_areas': dark_areas,
            'unusual_saturation': unusual_saturation,
            'color_variance': color_variance,
            'water_damage_pixels': np.sum(dark_areas),
            'color_inconsistency_pixels': np.sum(unusual_saturation),
            'severity': self.assess_color_severity(dark_areas, unusual_saturation, color_variance)
        }
    
    def assess_color_severity(self, dark_areas, unusual_saturation, color_variance):
        """Assess color-related issue severity"""
        dark_pixel_ratio = np.sum(dark_areas) / dark_areas.size
        unusual_pixel_ratio = np.sum(unusual_saturation) / unusual_saturation.size
        
        if dark_pixel_ratio > 0.1 or unusual_pixel_ratio > 0.15 or color_variance > 1000:
            return "Severe"
        elif dark_pixel_ratio > 0.05 or unusual_pixel_ratio > 0.08 or color_variance > 500:
            return "Moderate"
        elif dark_pixel_ratio > 0.02 or unusual_pixel_ratio > 0.04:
            return "Minor"
        else:
            return "None"
    
    def create_color_overlay(self, image, color_results):
        """Create color overlay showing detected issues"""
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        overlay = image.copy()
        
        # Blue overlay for dark areas (water damage)
        if color_results['dark_areas'] is not None:
            blue_mask = np.zeros_like(overlay)
            blue_mask[color_results['dark_areas']] = [0, 0, 255]
            overlay = cv2.addWeighted(overlay, 0.8, blue_mask, 0.2, 0)
        
        # Yellow overlay for color inconsistencies
        if color_results['unusual_saturation'] is not None:
            yellow_mask = np.zeros_like(overlay)
            yellow_mask[color_results['unusual_saturation']] = [255, 255, 0]
            overlay = cv2.addWeighted(overlay, 0.8, yellow_mask, 0.2, 0)
        
        return overlay
