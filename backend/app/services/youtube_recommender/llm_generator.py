"""
LLM-powered keyword generation for farming video searches.
Uses Google Gemini to generate contextual search terms.
"""

import google.generativeai as genai
from typing import Dict, List
import json

class LLMKeywordGenerator:
    """Generates search keywords using LLM based on crop context."""
    
    def __init__(self, api_key: str):
        """Initialize LLM client."""
        self.api_key = api_key
        
        if not api_key or api_key == 'your_gemini_api_key_here':
            raise ValueError("Gemini API key is required. Please configure GEMINI_API_KEY.")
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.enabled = True
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini LLM: {e}")
    
    def generate_keywords(self, stage_data: Dict) -> Dict:
        """
        Generate search keywords based on crop stage data.
        
        Args:
            stage_data: Dict containing stage info from stage detector
            
        Returns:
            Dict with primary_keywords, secondary_keywords, and search_terms
        """
        try:
            prompt = self._create_keyword_prompt(stage_data)
            response = self.model.generate_content(prompt)
            
            # Parse LLM response
            keywords = self._parse_llm_response(response.text)
            
            return keywords
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate keywords using LLM: {e}")
    
    def _create_keyword_prompt(self, stage_data: Dict) -> str:
        """Create a detailed prompt for keyword generation."""
        crop_type = stage_data.get('crop_type', 'unknown')
        stage = stage_data.get('stage_name', 'unknown')
        location = stage_data.get('location', 'India')
        days_since_sowing = stage_data.get('days_since_sowing', 0)
        recommendations = stage_data.get('recommendations', [])
        
        prompt = f"""
                    Generate YouTube search keywords for farming videos based on this context:

                    CROP DETAILS:
                    - Crop: {crop_type}
                    - Current Stage: {stage}
                    - Days since sowing: {days_since_sowing}
                    - Location: {location}

                    CURRENT RECOMMENDATIONS:
                    {chr(10).join(f"- {rec}" for rec in recommendations[:3])}

                    REQUIREMENTS:
                    1. Generate 8-10 primary keywords focused on current farming stage
                    2. Generate 5-8 secondary keywords for related topics
                    3. Include both English and Hindi terms where relevant
                    4. Focus on practical farming techniques and advice
                    5. Include location-specific terms if relevant

                    FORMAT your response as JSON:
                    {{
                        "primary_keywords": ["keyword1", "keyword2", ...],
                        "secondary_keywords": ["keyword1", "keyword2", ...],
                        "search_terms": ["complete search phrase 1", "complete search phrase 2", ...]
                    }}

                    Make keywords specific to {stage} stage of {crop_type} farming. Focus on actionable farming advice videos.
                    """
        return prompt
    
    def _parse_llm_response(self, response_text: str) -> Dict:
        """Parse LLM response and extract keywords."""
        try:
            # Try to parse as JSON
            if '{' in response_text and '}' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback parsing for non-JSON responses
                return self._extract_keywords_from_text(response_text)
                
        except json.JSONDecodeError:
            return self._extract_keywords_from_text(response_text)
    
    def _extract_keywords_from_text(self, text: str) -> Dict:
        """Extract keywords from unstructured text response."""
        lines = text.split('\n')
        primary_keywords = []
        secondary_keywords = []
        search_terms = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect sections
            if 'primary' in line.lower():
                current_section = 'primary'
                continue
            elif 'secondary' in line.lower():
                current_section = 'secondary'
                continue
            elif 'search' in line.lower():
                current_section = 'search'
                continue
            
            # Extract keywords from lines starting with - or numbers
            if line.startswith(('-', '*', '•')) or line[0].isdigit():
                keyword = line.lstrip('-*•0123456789. ').strip()
                if keyword:
                    if current_section == 'primary':
                        primary_keywords.append(keyword)
                    elif current_section == 'secondary':
                        secondary_keywords.append(keyword)
                    elif current_section == 'search':
                        search_terms.append(keyword)
        
        return {
            'primary_keywords': primary_keywords[:10],
            'secondary_keywords': secondary_keywords[:8],
            'search_terms': search_terms[:6]
        }
