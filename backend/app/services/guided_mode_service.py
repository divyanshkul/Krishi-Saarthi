"""
Service for AI-powered agricultural guidance system.
Integrates with Firebase for crop data and Gemini AI for guidance generation.
"""

import json
from typing import Any, Dict, Optional
from datetime import datetime
from app.core.config import settings
from app.utils.logger import get_logger
from app.services.youtube_recommender.firebase_client import FirebaseClient
from app.services.youtube_recommender.youtube_client import YouTubeClient
import google.generativeai as genai

logger = get_logger(__name__)

class GuidedModeService:
    """Service for generating AI-powered agricultural guidance"""
    
    def __init__(self):
        # Initialize Firebase client using existing pattern
        try:
            self.firebase_client = FirebaseClient(settings.firebase_config)
            logger.info("Firebase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase client: {e}")
            self.firebase_client = None
        
        # Initialize YouTube client
        try:
            if settings.YOUTUBE_API_KEY:
                self.youtube_client = YouTubeClient(settings.YOUTUBE_API_KEY)
                logger.info("YouTube client initialized successfully")
            else:
                logger.warning("YOUTUBE_API_KEY not configured")
                self.youtube_client = None
        except Exception as e:
            logger.error(f"Failed to initialize YouTube client: {e}")
            self.youtube_client = None
        
        # Initialize Gemini AI
        try:
            if settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini AI model (gemini-1.5-flash) initialized successfully")
            else:
                logger.error("GEMINI_API_KEY not configured")
                self.model = None
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            self.model = None
        
    async def get_crop_guidance(self, crop_name: str, farmer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive agricultural guidance for a specific crop
        
        Args:
            crop_name: Name of the crop to get guidance for
            farmer_id: Optional farmer ID to get personalized data from Firebase
            
        Returns:
            Dictionary containing guidance data or error information
        """
        try:
            logger.info(f"Generating guidance for crop: {crop_name}, farmer_id: {farmer_id}")
            
            # Get crop context from Firebase if farmer_id provided
            crop_context = None
            if farmer_id and self.firebase_client:
                try:
                    crops = self.firebase_client.get_farmer_crops(farmer_id)
                    crop_context = next((crop for crop in crops if crop.get('crop_type', '').lower() == crop_name.lower()), None)
                    logger.info(f"Found crop context from Firebase: {crop_context is not None}")
                except Exception as e:
                    logger.warning(f"Could not get crop context from Firebase: {e}")
            
            # Generate AI guidance using Gemini
            guidance_data = await self._generate_ai_guidance(crop_name, crop_context)
            
            # Enhance with real YouTube videos
            if self.youtube_client and guidance_data:
                guidance_data = await self._enhance_with_youtube_videos(guidance_data, crop_name)
            
            return {
                "success": True,
                "crop_name": crop_name,
                "stages": guidance_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating crop guidance: {e}")
            return {
                "success": False,
                "crop_name": crop_name,
                "stages": {},
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _generate_ai_guidance(self, crop_name: str, crop_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate comprehensive guidance using Gemini AI for all farming stages
        
        Args:
            crop_name: Name of the crop
            crop_context: Optional context from Firebase (sowing date, district, etc.)
            
        Returns:
            Dictionary containing structured guidance for all stages
        """
        if not self.model:
            logger.warning("Gemini AI not available, returning fallback guidance")
            return self._get_fallback_guidance(crop_name)
        
        prompt = self._create_comprehensive_prompt(crop_name, crop_context)
        
        try:
            logger.info("Sending request to Gemini AI")
            response = self.model.generate_content(prompt)
            
            # Parse the JSON response from Gemini
            guidance_text = response.text.strip()
            logger.debug(f"Received response from Gemini: {len(guidance_text)} characters")
            
            # More robust JSON extraction
            guidance_data = self._extract_json_from_response(guidance_text)
            if guidance_data:
                logger.info("Successfully parsed Gemini response as JSON")
                return guidance_data
            else:
                logger.error("Could not extract valid JSON from Gemini response")
                return self._get_fallback_guidance(crop_name)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.debug(f"Problematic text: {guidance_text[:500]}...")
            # Return fallback structure
            return self._get_fallback_guidance(crop_name)
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return self._get_fallback_guidance(crop_name)
    
    def _extract_json_from_response(self, text: str) -> Optional[Dict]:
        """
        Extract JSON from Gemini response, handling various formats and extra text
        
        Args:
            text: Raw response text from Gemini
            
        Returns:
            Parsed JSON dictionary or None if extraction fails
        """
        try:
            # Method 1: Try to parse as-is
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        try:
            # Method 2: Remove markdown code blocks
            if text.startswith('```json'):
                # Find the end of the JSON block
                end_marker = text.find('```', 7)
                if end_marker != -1:
                    json_text = text[7:end_marker].strip()
                else:
                    json_text = text[7:].strip()
                return json.loads(json_text)
            elif text.startswith('```'):
                # Generic code block
                end_marker = text.find('```', 3)
                if end_marker != -1:
                    json_text = text[3:end_marker].strip()
                else:
                    json_text = text[3:].strip()
                return json.loads(json_text)
        except json.JSONDecodeError:
            pass
        
        try:
            # Method 3: Find JSON object by looking for { and }
            first_brace = text.find('{')
            if first_brace != -1:
                # Count braces to find the complete JSON object
                brace_count = 0
                end_pos = first_brace
                
                for i, char in enumerate(text[first_brace:], first_brace):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_pos = i + 1
                            break
                
                if brace_count == 0:
                    json_text = text[first_brace:end_pos]
                    return json.loads(json_text)
        except json.JSONDecodeError:
            pass
        
        # Method 4: Try to find the largest valid JSON substring
        try:
            # Look for the pattern that starts with { and try progressively smaller substrings
            first_brace = text.find('{')
            if first_brace != -1:
                for end_pos in range(len(text), first_brace, -1):
                    try:
                        candidate = text[first_brace:end_pos].strip()
                        if candidate.endswith('}'):
                            return json.loads(candidate)
                    except json.JSONDecodeError:
                        continue
        except:
            pass
        
        logger.error("All JSON extraction methods failed")
        return None
    
    async def _enhance_with_youtube_videos(self, guidance_data: Dict[str, Any], crop_name: str) -> Dict[str, Any]:
        """
        Enhance guidance data with actual YouTube video links for relevant topics
        
        Args:
            guidance_data: The guidance data from Gemini AI
            crop_name: Name of the crop for context
            
        Returns:
            Enhanced guidance data with real YouTube videos
        """
        if not self.youtube_client:
            logger.warning("YouTube client not available, skipping video enhancement")
            return guidance_data
        
        try:
            logger.info(f"Enhancing guidance with YouTube videos for {crop_name}")
            
            # Define topics that should have videos (2 videos per stage max)
            video_topics = {
                'soilPrep': ['Plowing', 'Soil Testing', 'Land Preparation'],
                'seedSowing': ['Sowing', 'Seed Treatment'],
                'cropGrowth': ['Irrigation', 'Fertilizer Application'],
                'harvesting': ['Harvesting Techniques'],
                'postHarvest': ['Storage Methods']
            }
            
            # Process each stage
            for stage_key, stage_data in guidance_data.items():
                if stage_key not in video_topics:
                    continue
                    
                topics = stage_data.get('topics', [])
                if not topics:
                    continue
                
                # Select up to 2 relevant topics for videos
                relevant_topics = video_topics[stage_key]
                video_count = 0
                max_videos_per_stage = 2
                
                for topic in topics:
                    if video_count >= max_videos_per_stage:
                        break
                        
                    topic_title = topic.get('title', '')
                    
                    # Check if this topic should have videos
                    should_add_videos = any(
                        relevant_keyword.lower() in topic_title.lower() 
                        for relevant_keyword in relevant_topics
                    )
                    
                    if should_add_videos:
                        # Generate search terms for this specific topic
                        search_keywords = self._generate_search_keywords(crop_name, topic_title, stage_key)
                        
                        # Search for videos
                        try:
                            videos = self.youtube_client.search_videos(search_keywords, max_results=3, min_results=1)
                            
                            if videos:
                                # Take the best 1-2 videos
                                selected_videos = videos[:2]
                                video_links = [video['url'] for video in selected_videos]
                                
                                # Update the topic with real video links
                                topic['video_links'] = video_links
                                video_count += 1
                                
                                logger.info(f"Added {len(video_links)} videos for topic: {topic_title}")
                            else:
                                # Keep empty list if no videos found
                                topic['video_links'] = []
                                
                        except Exception as e:
                            logger.error(f"Error searching videos for topic {topic_title}: {e}")
                            topic['video_links'] = []
                    else:
                        # Ensure topics without videos have empty list
                        if 'video_links' not in topic:
                            topic['video_links'] = []
                
                logger.info(f"Enhanced {video_count} topics with videos in {stage_key} stage")
            
            return guidance_data
            
        except Exception as e:
            logger.error(f"Error enhancing guidance with YouTube videos: {e}")
            return guidance_data
    
    def _generate_search_keywords(self, crop_name: str, topic_title: str, stage_key: str) -> Dict[str, list]:
        """
        Generate search keywords for YouTube video search
        
        Args:
            crop_name: Name of the crop
            topic_title: Title of the topic
            stage_key: Stage key (soilPrep, seedSowing, etc.)
            
        Returns:
            Dictionary with search keywords for YouTube API
        """
        # Base search terms combining crop and topic
        primary_keywords = [
            f"{crop_name} {topic_title}",
            f"{crop_name} farming {topic_title}",
            f"{topic_title} {crop_name} cultivation"
        ]
        
        # Stage-specific keywords
        stage_keywords = {
            'soilPrep': ['soil preparation', 'land preparation', 'plowing', 'मिट्टी तैयारी'],
            'seedSowing': ['seed sowing', 'sowing technique', 'बुआई', 'बीज बोना'],
            'cropGrowth': ['crop management', 'fertilizer application', 'irrigation', 'फसल प्रबंधन'],
            'harvesting': ['harvesting technique', 'crop harvesting', 'कटाई'],
            'postHarvest': ['storage method', 'post harvest', 'भंडारण']
        }
        
        secondary_keywords = []
        if stage_key in stage_keywords:
            for keyword in stage_keywords[stage_key]:
                secondary_keywords.extend([
                    f"{crop_name} {keyword}",
                    f"{keyword} farming",
                    keyword
                ])
        
        # Search terms for YouTube API
        search_terms = [
            f"{crop_name} farming {topic_title}",
            f"{crop_name} cultivation",
            f"{topic_title} farming technique",
            f"{crop_name} agriculture"
        ]
        
        return {
            'primary_keywords': primary_keywords[:5],
            'secondary_keywords': secondary_keywords[:5],
            'search_terms': search_terms[:4]
        }
    
    def _create_comprehensive_prompt(self, crop_name: str, crop_context: Optional[Dict] = None) -> str:
        """
        Create a comprehensive prompt for generating crop guidance
        
        Args:
            crop_name: Name of the crop
            crop_context: Optional context from Firebase
            
        Returns:
            Formatted prompt string for Gemini AI
        """
        context_info = ""
        if crop_context:
            context_info = f"""
    Additional context from farmer's data:
    - District: {crop_context.get('district', 'Not specified')}
    - State: {crop_context.get('state', 'Not specified')}
    """
            
            return f"""
    You are an expert agricultural advisor specializing in Indian farming practices. Generate comprehensive guidance for {crop_name} cultivation specifically for Indian farmers.

    {context_info}

    IMPORTANT INSTRUCTIONS:
    1. Focus on Indian agricultural context, climate, and farming practices
    2. Provide comprehensive guidance but DO NOT include specific YouTube video links
    3. Include article links for detailed reading and government resources when possible
    4. Prioritize practical, actionable guidance with specific measurements and timings
    5. Consider regional variations in India (North, South, West, East)
    6. Include cost-effective solutions suitable for small and medium farmers
    7. Focus on educational content that would benefit from video demonstrations
    8. Mention when visual learning would be helpful, but don't provide video URLs

    ARTICLE LINK GUIDELINES:
    - Include government agricultural extension resources when possible
    - Link to research papers and farming guides
    - Include market information and pricing resources
    - Provide links to agricultural schemes and subsidies

    Generate a JSON response with the following structure. RESPOND ONLY WITH VALID JSON, NO ADDITIONAL TEXT OR EXPLANATIONS:

    {{
    "soilPrep": {{
        "stage_name": "Soil Preparation",
        "stage_type": "soil_preparation",
        "topics": [
        {{
            "title": "Plowing Depth and Technique",
            "icon": "plow",
            "description": "Detailed guidance on optimal plowing depth for {crop_name} in Indian soil conditions. Include specific depth measurements (15-20 cm for {crop_name}), timing based on monsoon patterns, and soil moisture requirements. For clay soils, deep plowing improves aeration. For sandy soils, moderate plowing prevents nutrient loss. Visual demonstrations of proper plowing techniques are highly beneficial for farmers.",
            "articles": ["Include government soil preparation guidelines when available"]
        }},
        {{
            "title": "Soil Testing and pH Management",
            "icon": "science",
            "description": "Soil testing procedures available at government centers, optimal pH range for {crop_name} (specify exact range), and cost-effective amendments for Indian soil types. Include organic matter improvement techniques using locally available materials.",
            "articles": ["Include government soil testing center locations and procedures when available"]
        }}
        ]
    }},
    "seedSowing": {{
        "stage_name": "Seed Sowing",
        "stage_type": "seed_sowing", 
        "topics": [
        {{
            "title": "Optimal Sowing Time",
            "icon": "schedule",
            "description": "Best sowing time for {crop_name} in different Indian regions (Kharif/Rabi season), considering monsoon patterns and regional climate variations. Include specific dates for North (Oct-Nov), Central (Nov), and South India (Nov-Dec) regions. Visual calendar demonstrations help farmers understand timing.",
            "articles": ["Include government sowing advisories and weather-based recommendations when available"]
        }},
        {{
            "title": "Seed Treatment and Spacing",
            "icon": "grain",
            "description": "Seed treatment methods to prevent diseases using affordable fungicides available in India, optimal spacing between seeds (specify in cm), row spacing for {crop_name}, and seed rate per acre. Include traditional and modern techniques. Practical demonstrations of seed treatment and sowing are valuable.",
            "articles": ["Include seed treatment chemical guidelines and spacing recommendations when available"]
        }}
        ]
    }},
    "cropGrowth": {{
        "stage_name": "Crop Growth Management",
        "stage_type": "crop_growth",
        "topics": [
        {{
            "title": "Irrigation Schedule",
            "icon": "water_drop",
            "description": "Detailed irrigation schedule for {crop_name} considering Indian water availability, critical growth stages requiring water, drip vs flood irrigation comparison, and water conservation techniques. Include rainfall dependency and drought management. Visual demonstrations of irrigation setups are essential.",
            "articles": ["Include government irrigation schemes and water management guidelines when available"]
        }},
        {{
            "title": "Fertilizer and Nutrient Management",
            "icon": "eco",
            "description": "Specific fertilizer recommendations with quantities per acre (N-P-K ratios for {crop_name}), timing of application (basal, top-dressing), cost per acre, and organic alternatives like vermicompost and farm yard manure available in India. Practical application techniques benefit from visual learning.",
            "articles": ["Include government fertilizer subsidy schemes and nutrient management guides when available"]
        }},
        {{
            "title": "Pest and Disease Management",
            "icon": "bug_report",
            "description": "Common pests and diseases affecting {crop_name} in India, visual identification methods, treatment options including government-approved pesticides, organic solutions like neem oil, and IPM practices suitable for Indian conditions.",
            "articles": ["Include government pest management advisories and approved pesticide lists when available"]
        }}
        ]
    }},
    "harvesting": {{
        "stage_name": "Harvesting",
        "stage_type": "harvesting",
        "topics": [
        {{
            "title": "Maturity Indicators",
            "icon": "visibility",
            "description": "Visual and physical indicators to determine when {crop_name} is ready for harvest, including moisture content guidelines (specify %), color changes, and field tests that farmers can perform without equipment. Visual identification guides are extremely helpful.",
            "articles": ["Include harvesting timing guides and maturity indicator charts when available"]
        }},
        {{
            "title": "Harvesting Techniques",
            "icon": "cut",
            "description": "Optimal harvesting methods for {crop_name} (manual vs mechanical), best time of day for harvesting, weather considerations, and immediate post-harvest handling to minimize losses. Include cost comparison of different methods. Practical harvesting demonstrations are valuable.",
            "articles": ["Include government harvesting machinery schemes and cost-benefit analysis when available"]
        }}
        ]
    }},
    "postHarvest": {{
        "stage_name": "Post-Harvest Management",
        "stage_type": "post_harvest",
        "topics": [
        {{
            "title": "Storage and Preservation",
            "icon": "inventory",
            "description": "Proper storage methods for {crop_name} to prevent pest infestation and maintain quality, including traditional Indian storage techniques (kothar, metal bins), moisture control, and fumigation methods. Include cost-effective solutions for small farmers. Storage setup demonstrations are practical.",
            "articles": ["Include government storage scheme guidelines and warehouse facilities when available"]
        }},
        {{
            "title": "Market Information and Pricing",
            "icon": "trending_up",
            "description": "Current market trends for {crop_name} in Indian mandis, seasonal price patterns, government MSP (Minimum Support Price) information, best time to sell for maximum profit, and alternative marketing channels including FPOs.",
            "articles": ["Include e-NAM portal links when available", "Include current MSP and market price information", "Include government marketing scheme details when available"]
        }}
        ]
    }}
    }}

    Provide practical, region-specific advice that Indian farmers can actually implement with locally available resources and within typical budget constraints of Indian agriculture.

    CRITICAL: Return ONLY the JSON response above. Do not include any explanatory text, markdown formatting, or additional content outside the JSON structure.
    """
    
    def _get_fallback_guidance(self, crop_name: str) -> Dict[str, Any]:
        """
        Provide fallback guidance structure when AI generation fails
        
        Args:
            crop_name: Name of the crop
            
        Returns:
            Basic guidance structure with fallback content
        """
        logger.info(f"Providing fallback guidance for {crop_name}")
        
        return {
            "soilPrep": {
                "stage_name": "Soil Preparation",
                "stage_type": "soil_preparation",
                "topics": [
                    {
                        "title": "Basic Soil Preparation",
                        "icon": "plow",
                        "description": f"Prepare soil for {crop_name} by plowing to appropriate depth (15-20 cm) and ensuring proper drainage. Test soil pH and add organic matter to improve soil health.",
                        "video_links": [],
                        "articles": []
                    },
                    {
                        "title": "Soil Health Management",
                        "icon": "science",
                        "description": f"Conduct soil testing to understand nutrient requirements for {crop_name}. Add compost or farmyard manure to improve soil structure and fertility.",
                        "video_links": [],
                        "articles": []
                    }
                ]
            },
            "seedSowing": {
                "stage_name": "Seed Sowing", 
                "stage_type": "seed_sowing",
                "topics": [
                    {
                        "title": "Sowing Guidelines",
                        "icon": "grain",
                        "description": f"Follow recommended sowing practices for {crop_name} including proper spacing, depth, and timing. Use quality seeds and treat them before sowing.",
                        "video_links": [],
                        "articles": []
                    },
                    {
                        "title": "Seed Treatment",
                        "icon": "science",
                        "description": f"Treat seeds with appropriate fungicides to prevent soil-borne diseases. Follow recommended seed rate for optimal plant population of {crop_name}.",
                        "video_links": [],
                        "articles": []
                    }
                ]
            },
            "cropGrowth": {
                "stage_name": "Crop Growth Management",
                "stage_type": "crop_growth", 
                "topics": [
                    {
                        "title": "Irrigation Management",
                        "icon": "water_drop",
                        "description": f"Provide adequate water to {crop_name} at critical growth stages. Monitor soil moisture and avoid water stress during flowering and grain filling.",
                        "video_links": [],
                        "articles": []
                    },
                    {
                        "title": "Nutrient Management",
                        "icon": "eco",
                        "description": f"Apply balanced fertilizers based on soil test recommendations for {crop_name}. Use organic sources like compost to supplement chemical fertilizers.",
                        "video_links": [],
                        "articles": []
                    },
                    {
                        "title": "Pest Management",
                        "icon": "bug_report",
                        "description": f"Monitor {crop_name} regularly for pests and diseases. Use integrated pest management approaches including biological and chemical controls.",
                        "video_links": [],
                        "articles": []
                    }
                ]
            },
            "harvesting": {
                "stage_name": "Harvesting",
                "stage_type": "harvesting",
                "topics": [
                    {
                        "title": "Harvest Timing",
                        "icon": "cut", 
                        "description": f"Harvest {crop_name} at optimal maturity for best quality and yield. Check for proper moisture content and visual indicators of maturity.",
                        "video_links": [],
                        "articles": []
                    },
                    {
                        "title": "Harvesting Methods",
                        "icon": "visibility",
                        "description": f"Use appropriate harvesting techniques for {crop_name} to minimize losses. Handle harvested produce carefully to maintain quality.",
                        "video_links": [],
                        "articles": []
                    }
                ]
            },
            "postHarvest": {
                "stage_name": "Post-Harvest Management",
                "stage_type": "post_harvest",
                "topics": [
                    {
                        "title": "Storage Management",
                        "icon": "inventory",
                        "description": f"Store {crop_name} properly to maintain quality and prevent losses. Use clean, dry storage facilities and monitor for pest infestation.",
                        "video_links": [],
                        "articles": []
                    },
                    {
                        "title": "Market Planning",
                        "icon": "trending_up",
                        "description": f"Plan marketing strategy for {crop_name} to get better prices. Monitor market prices and choose optimal timing for sale.",
                        "video_links": [],
                        "articles": ["Check government mandi prices and MSP information"]
                    }
                ]
            }
        }
    
    def is_healthy(self) -> Dict[str, Any]:
        """
        Check the health status of the service
        
        Returns:
            Dictionary containing health status information
        """
        return {
            "firebase_connected": self.firebase_client is not None and self.firebase_client.is_connected(),
            "gemini_configured": self.model is not None,
            "youtube_configured": self.youtube_client is not None,
            "service_ready": self.model is not None
        }
