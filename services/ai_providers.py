"""
External AI providers for enhanced wall damage analysis
Supports OpenAI GPT-4V, Google Gemini, and other vision models
"""

import streamlit as st
import base64
import requests
import json
from typing import Dict, List, Optional, Tuple
from PIL import Image
import io

class AIProvider:
    """Base class for AI providers"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def analyze_wall_image(self, image: Image.Image, basic_analysis: Dict) -> Dict:
        """Analyze wall image and return enhanced results"""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Check if the provider is properly configured"""
        return bool(self.api_key)

class OpenAIProvider(AIProvider):
    """OpenAI GPT-4V provider for wall damage analysis"""
    
    def __init__(self, api_key: str):
        # Clean the API key to remove any trailing whitespace
        clean_key = api_key.strip()
        super().__init__(clean_key)
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4-vision-preview"
    
    def encode_image(self, image: Image.Image) -> str:
        """Encode PIL image to base64"""
        try:
            buffer = io.BytesIO()
            
            # Ensure image is in RGB mode
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image to reduce API costs and ensure valid dimensions
            max_size = 1024
            if max(image.size) > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Ensure minimum size to avoid API issues
            if min(image.size) < 32:
                image = image.resize((max(32, image.size[0]), max(32, image.size[1])), Image.Resampling.LANCZOS)
            
            image.save(buffer, format="JPEG", quality=85)
            return base64.b64encode(buffer.getvalue()).decode()
            
        except Exception as e:
            raise ValueError(f"Failed to encode image: {str(e)}")
    
    def analyze_wall_image(self, image: Image.Image, basic_analysis: Dict) -> Dict:
        """Analyze wall image using GPT-4V"""
        try:
            base64_image = self.encode_image(image)
            
            # Create analysis prompt based on basic analysis
            basic_summary = self.create_basic_summary(basic_analysis)
            
            prompt = f"""You are a professional building inspector analyzing a wall for damage. 

Basic computer vision analysis detected:
{basic_summary}

Please analyze this wall image and provide:

1. **Damage Assessment**: Confirm or refine the detected issues
2. **Severity Rating**: Rate each issue (Minor/Moderate/Severe)
3. **Root Causes**: Likely causes for each type of damage
4. **Repair Recommendations**: Specific steps to fix each issue
5. **Cost Estimates**: Rough cost ranges for repairs
6. **Priority**: Which issues should be addressed first

Format your response as JSON with this structure:
{{
  "overall_condition": "Good/Fair/Poor",
  "detected_issues": [
    {{
      "type": "crack/water_damage/nail_pop/color_inconsistency",
      "severity": "Minor/Moderate/Severe",
      "location": "description of where on the wall",
      "likely_cause": "explanation",
      "repair_method": "specific repair steps",
      "estimated_cost": "cost range",
      "priority": "High/Medium/Low"
    }}
  ],
  "professional_notes": "additional observations",
  "immediate_actions": ["list of urgent actions if any"]
}}

Be thorough but practical in your assessment."""

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.1
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Try to parse JSON response
            try:
                analysis = json.loads(content)
                analysis['provider'] = 'OpenAI GPT-4V'
                analysis['success'] = True
                return analysis
            except json.JSONDecodeError:
                # If JSON parsing fails, return text analysis
                return {
                    'provider': 'OpenAI GPT-4V',
                    'success': True,
                    'raw_analysis': content,
                    'overall_condition': 'Unknown',
                    'detected_issues': [],
                    'professional_notes': content
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'provider': 'OpenAI GPT-4V',
                'success': False,
                'error': f"API request failed: {str(e)}"
            }
        except Exception as e:
            return {
                'provider': 'OpenAI GPT-4V',
                'success': False,
                'error': f"Analysis failed: {str(e)}"
            }
    
    def create_basic_summary(self, basic_analysis: Dict) -> str:
        """Create a summary of basic computer vision analysis"""
        try:
            summary = []
            
            # Safely extract values with defaults and validation
            cracks = max(0, int(basic_analysis.get('cracks', 0)))
            if cracks > 0:
                summary.append(f"- {cracks} potential cracks detected")
            
            nail_pops = max(0, int(basic_analysis.get('nail_pops', 0)))
            if nail_pops > 0:
                summary.append(f"- {nail_pops} potential nail pops detected")
            
            water_damage_pixels = max(0, int(basic_analysis.get('water_damage_pixels', 0)))
            if water_damage_pixels > 1000:
                summary.append(f"- {water_damage_pixels:,} pixels showing potential water damage")
            
            color_inconsistency_pixels = max(0, int(basic_analysis.get('color_inconsistency_pixels', 0)))
            if color_inconsistency_pixels > 2000:
                summary.append(f"- {color_inconsistency_pixels:,} pixels with color inconsistencies")
            
            # Add severity information if available
            if basic_analysis.get('crack_severity') and basic_analysis['crack_severity'] != 'None':
                summary.append(f"- Crack severity: {basic_analysis['crack_severity']}")
            
            if basic_analysis.get('nail_pop_severity') and basic_analysis['nail_pop_severity'] != 'None':
                summary.append(f"- Nail pop severity: {basic_analysis['nail_pop_severity']}")
            
            if basic_analysis.get('color_severity') and basic_analysis['color_severity'] != 'None':
                summary.append(f"- Color issue severity: {basic_analysis['color_severity']}")
            
            return '\n'.join(summary) if summary else "- No significant issues detected by computer vision"
            
        except Exception as e:
            # If basic analysis summary creation fails, provide a safe fallback
            return f"- Basic computer vision analysis completed (details unavailable due to processing error: {str(e)})"

class GeminiProvider(AIProvider):
    """Google Gemini provider for wall damage analysis"""
    
    def __init__(self, api_key: str):
        # Clean the API key to remove any trailing whitespace or backslashes
        clean_key = api_key.strip().rstrip('\\')
        super().__init__(clean_key)
        self.base_url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"
    
    def encode_image(self, image: Image.Image) -> str:
        """Encode PIL image to base64"""
        try:
            buffer = io.BytesIO()
            
            # Ensure image is in RGB mode
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image to reduce API costs and ensure valid dimensions
            max_size = 1024
            if max(image.size) > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Ensure minimum size to avoid API issues
            if min(image.size) < 32:
                image = image.resize((max(32, image.size[0]), max(32, image.size[1])), Image.Resampling.LANCZOS)
            
            image.save(buffer, format="JPEG", quality=85)
            return base64.b64encode(buffer.getvalue()).decode()
            
        except Exception as e:
            raise ValueError(f"Failed to encode image: {str(e)}")
    
    def analyze_wall_image(self, image: Image.Image, basic_analysis: Dict) -> Dict:
        """Analyze wall image using Gemini Pro Vision"""
        try:
            base64_image = self.encode_image(image)
            
            # Create analysis prompt
            basic_summary = self.create_basic_summary(basic_analysis)
            
            prompt = f"""As a professional building inspector, analyze this wall image for damage and defects.

Computer vision pre-analysis results:
{basic_summary}

Please provide a detailed assessment including:
1. Confirmation or correction of detected issues
2. Severity assessment (Minor/Moderate/Severe)
3. Likely causes and repair recommendations
4. Cost estimates and priority levels

Focus on: cracks, nail pops, water damage, paint issues, and structural concerns.

Provide practical, actionable advice for homeowners."""

            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "topK": 32,
                    "topP": 1,
                    "maxOutputTokens": 1500
                }
            }
            
            # Construct URL with cleaned API key
            url = f"{self.base_url}?key={self.api_key}"
            
            response = requests.post(
                url, 
                headers=headers, 
                json=payload, 
                timeout=30
            )
            
            # Check for errors
            if response.status_code != 200:
                error_detail = response.text[:500] if response.text else "No error details"
                raise requests.exceptions.RequestException(
                    f"Status {response.status_code}: {error_detail}"
                )
            
            response.raise_for_status()
            
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            
            return {
                'provider': 'Google Gemini 2.5 Flash',
                'success': True,
                'professional_notes': content,
                'overall_condition': 'Analyzed',
                'detected_issues': [],
                'raw_analysis': content
            }
                
        except requests.exceptions.RequestException as e:
            return {
                'provider': 'Google Gemini 2.5 Flash',
                'success': False,
                'error': f"API request failed: {str(e)}"
            }
        except Exception as e:
            return {
                'provider': 'Google Gemini 2.5 Flash',
                'success': False,
                'error': f"Analysis failed: {str(e)}"
            }
    
    def create_basic_summary(self, basic_analysis: Dict) -> str:
        """Create a summary of basic computer vision analysis"""
        try:
            summary = []
            
            # Safely extract values with defaults and validation
            cracks = max(0, int(basic_analysis.get('cracks', 0)))
            if cracks > 0:
                summary.append(f"- {cracks} potential cracks detected")
            
            nail_pops = max(0, int(basic_analysis.get('nail_pops', 0)))
            if nail_pops > 0:
                summary.append(f"- {nail_pops} potential nail pops detected")
            
            water_damage_pixels = max(0, int(basic_analysis.get('water_damage_pixels', 0)))
            if water_damage_pixels > 1000:
                summary.append(f"- Water damage indicators in {water_damage_pixels:,} pixels")
            
            color_inconsistency_pixels = max(0, int(basic_analysis.get('color_inconsistency_pixels', 0)))
            if color_inconsistency_pixels > 2000:
                summary.append(f"- Color variations in {color_inconsistency_pixels:,} pixels")
            
            # Add severity information if available
            if basic_analysis.get('crack_severity') and basic_analysis['crack_severity'] != 'None':
                summary.append(f"- Crack severity: {basic_analysis['crack_severity']}")
            
            if basic_analysis.get('nail_pop_severity') and basic_analysis['nail_pop_severity'] != 'None':
                summary.append(f"- Nail pop severity: {basic_analysis['nail_pop_severity']}")
            
            if basic_analysis.get('color_severity') and basic_analysis['color_severity'] != 'None':
                summary.append(f"- Color issue severity: {basic_analysis['color_severity']}")
            
            return '\n'.join(summary) if summary else "- No significant issues detected by computer vision"
            
        except Exception as e:
            # If basic analysis summary creation fails, provide a safe fallback
            return f"- Basic computer vision analysis completed (details unavailable due to processing error: {str(e)})"

def get_available_providers(openai_key: str = None, gemini_key: str = None) -> Dict[str, AIProvider]:
    """Get available AI providers based on provided API keys"""
    providers = {}
    
    if openai_key:
        providers['OpenAI GPT-4V'] = OpenAIProvider(openai_key)
    
    if gemini_key:
        providers['Google Gemini'] = GeminiProvider(gemini_key)
    
    return providers

def analyze_with_ai(provider: AIProvider, image: Image.Image, basic_analysis: Dict) -> Dict:
    """Analyze image with the selected AI provider"""
    if not provider.is_available():
        return {
            'success': False,
            'error': 'Provider not properly configured'
        }
    
    return provider.analyze_wall_image(image, basic_analysis)
