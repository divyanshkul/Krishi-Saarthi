"""
LLM-Powered Crop Stage Detector
Uses Gemini LLM to intelligently detect farming stages for any crop.
"""

from datetime import datetime
from typing import Dict, Optional
import google.generativeai as genai
import json
import re

class CropStageDetector:
    """LLM-powered crop stage detection for any crop type."""
    
    def __init__(self, gemini_api_key: str):
        """Initialize LLM-based stage detector."""
        if not gemini_api_key or gemini_api_key == "your_gemini_api_key_here":
            raise ValueError("Gemini API key is required for stage detection")
        
        try:
            genai.configure(api_key=gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.enabled = True
        except Exception as e:
            raise ValueError(f"Failed to initialize LLM: {e}")
    
    def detect_stage(self, crop_data: Dict) -> Dict:
        """
        Use LLM to detect current farming stage for any crop.
        
        Args:
            crop_data: Dictionary with crop_type, sowing_date, district, state
            
        Returns:
            Dictionary with stage information
        """
        crop_type = crop_data.get('crop_type', '').lower()
        sowing_date_str = crop_data.get('sowing_date')
        district = crop_data.get('district', 'Unknown')
        state = crop_data.get('state', 'Unknown')
        
        if not crop_type or not sowing_date_str:
            return self._unknown_stage_response(crop_data)
        
        try:
            # Calculate days since sowing
            sowing_date = datetime.strptime(sowing_date_str, '%Y-%m-%d').date()
            current_date = datetime.now().date()
            days_since_sowing = (current_date - sowing_date).days
            
            # Create prompt for LLM
            prompt = self._create_stage_detection_prompt(
                crop_type, days_since_sowing, district, state
            )
            
            # Get LLM response
            response = self.model.generate_content(prompt)
            stage_info = self._parse_llm_response(response.text, crop_data, days_since_sowing)
            
            return stage_info
            
        except Exception as e:
            return self._fallback_stage_detection(crop_data, days_since_sowing if 'days_since_sowing' in locals() else 0)
    
    def _create_stage_detection_prompt(self, crop_type: str, days_since_sowing: int, 
                                     district: str, state: str) -> str:
        """Create prompt for LLM stage detection."""
        
        current_month = datetime.now().strftime("%B")
        
        prompt = f"""
You are an expert agricultural consultant. Analyze the farming stage for this crop:

CROP INFORMATION:
- Crop: {crop_type}
- Days since sowing: {days_since_sowing}
- Location: {district}, {state}
- Current month: {current_month}

TASK: Determine the current farming stage and provide recommendations.

Consider:
1. Typical growth cycle for {crop_type}
2. Climate conditions in {state}
3. Regional farming practices
4. Season-specific factors

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "stage_name": "stage_name",
    "stage_description": "brief description",
    "confidence": 0.85,
    "recommendations": ["recommendation1", "recommendation2"]
}}

COMMON FARMING STAGES:
- germination (0-10 days)
- seedling (10-25 days)
- vegetative (25-60 days)
- flowering/reproductive (varies by crop)
- fruit_development (for fruiting crops)
- maturity/harvest_ready (final stage)

Provide practical, actionable advice for farmers in {state}.
"""
        return prompt
    
    def _parse_llm_response(self, llm_response: str, crop_data: Dict, 
                           days_since_sowing: int) -> Dict:
        """Parse LLM response into structured format."""
        
        try:
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                stage_data = json.loads(json_str)
            else:
                # Fallback parsing if JSON not found
                stage_data = self._extract_stage_info_from_text(llm_response)
            
            # Structure the response
            response = {
                'stage_name': stage_data.get('stage_name', 'unknown'),
                'stage_description': stage_data.get('stage_description', ''),
                'days_since_sowing': days_since_sowing,
                'confidence': float(stage_data.get('confidence', 0.7)),
                'detection_method': 'llm_analysis',
                'crop_type': crop_data.get('crop_type'),
                'location': f"{crop_data.get('district', 'Unknown')}, {crop_data.get('state', 'Unknown')}",
                'recommendations': stage_data.get('recommendations', [])
            }
            
            return response
            
        except Exception as e:
            return self._fallback_stage_detection(crop_data, days_since_sowing)
    
    def _extract_stage_info_from_text(self, text: str) -> Dict:
        """Extract stage information from free text if JSON parsing fails."""
        
        # Simple text-based extraction
        stage_keywords = {
            'germination': ['germination', 'sprouting', 'emergence'],
            'seedling': ['seedling', 'early growth', 'establishment'],
            'vegetative': ['vegetative', 'growth', 'leafing'],
            'flowering': ['flowering', 'bloom', 'reproductive'],
            'fruit_development': ['fruit', 'development', 'formation'],
            'maturity': ['maturity', 'harvest', 'ripening']
        }
        
        text_lower = text.lower()
        detected_stage = 'unknown'
        
        for stage, keywords in stage_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_stage = stage
                break
        
        return {
            'stage_name': detected_stage,
            'stage_description': f'Stage detected from text analysis',
            'confidence': 0.6,
            'recommendations': ['Monitor crop development']
        }
    
    def _fallback_stage_detection(self, crop_data: Dict, days_since_sowing: int) -> Dict:
        """Fallback stage detection based on simple rules."""
        
        # Simple rule-based fallback
        if days_since_sowing <= 10:
            stage = 'germination'
            recommendations = ['Ensure adequate moisture', 'Protect from pests']
        elif days_since_sowing <= 30:
            stage = 'seedling'
            recommendations = ['Monitor growth', 'Light fertilization']
        elif days_since_sowing <= 60:
            stage = 'vegetative'
            recommendations = ['Regular watering', 'Nutrient management']
        elif days_since_sowing <= 90:
            stage = 'reproductive'
            recommendations = ['Support flowering', 'Pest control']
        else:
            stage = 'maturity'
            recommendations = ['Prepare for harvest', 'Monitor ripeness']
        
        return {
            'stage_name': stage,
            'stage_description': f'Estimated stage based on days since sowing',
            'days_since_sowing': days_since_sowing,
            'confidence': 0.5,
            'detection_method': 'rule_based_fallback',
            'crop_type': crop_data.get('crop_type'),
            'location': f"{crop_data.get('district', 'Unknown')}, {crop_data.get('state', 'Unknown')}",
            'recommendations': recommendations
        }
    
    def _unknown_stage_response(self, crop_data: Dict, days_since_sowing: int = 0) -> Dict:
        """Return unknown stage response."""
        return {
            'stage_name': 'unknown',
            'stage_description': 'Unable to determine stage',
            'days_since_sowing': days_since_sowing,
            'confidence': 0.0,
            'detection_method': 'insufficient_data',
            'crop_type': crop_data.get('crop_type', 'unknown'),
            'location': f"{crop_data.get('district', 'Unknown')}, {crop_data.get('state', 'Unknown')}",
            'recommendations': ['Provide complete crop information'],
            'error': 'Insufficient crop data for stage detection'
        }

    def get_status(self) -> Dict:
        """Get detector status."""
        return {
            'enabled': self.enabled,
            'detection_method': 'llm_powered',
            'model': 'gemini-2.0-flash-exp',
            'supports_any_crop': True
        }
