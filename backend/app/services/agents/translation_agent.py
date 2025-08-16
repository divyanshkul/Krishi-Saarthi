import os
import time
import json
from openai import OpenAI
from app.utils.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class TranslationAgent:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def process_audio(self, audio_path: str) -> dict:
        logger.info("======== Starting Translation Pipeline ========")
        logger.info(f"Processing audio file: {audio_path}")
        
        try:
            # Stage 1: Transcribe audio
            transcription = await self.transcribe_audio(audio_path)
            if not transcription:
                logger.error("Error: Transcription failed")
                return self._create_error_response("Transcription failed")
            
            # Stage 2: Enhancement with agricultural context
            enhancement = await self.enhance_transcription(transcription)
            if not enhancement:
                logger.error("Error: Enhancement failed")
                return self._create_fallback_response(transcription)
            
            # Combine results
            result = {
                "success": True,
                "original_transcription": transcription,
                "translation": enhancement.get("translation", transcription),
                "agricultural_terms": enhancement.get("agricultural_terms", []),
                "confidence": enhancement.get("confidence", "Low"),
                "reasoning": enhancement.get("reasoning", "")
            }
            
            logger.info("======== Translation Complete ========")
            logger.info(f"Translation: {result['translation']}")
            logger.info(f"Agricultural terms: {', '.join(result['agricultural_terms'])}")
            logger.info(f"Confidence: {result['confidence']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error: Translation pipeline failed - {str(e)}")
            return self._create_error_response(str(e))
    
    async def transcribe_audio(self, audio_path: str) -> str:
        logger.info("======== Stage 1: Transcription ========")
        
        try:
            start_time = time.time()
            
            with open(audio_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="gpt-4o-transcribe",
                    file=audio_file,
                    response_format="json",
                    prompt="The following is a conversation about agriculture, farming, crops, and agricultural practices in Hindi and English."
                )
            
            end_time = time.time()
            transcription = response.text
            
            logger.info(f"Transcription time: {end_time - start_time:.2f}s")
            logger.info(f"Result: {transcription}")
            return transcription
            
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return None
    
    async def enhance_transcription(self, transcription: str) -> dict:
        logger.info("======== Stage 2: Enhancement ========")
        logger.info("Translating and extracting agricultural context...")
        
        try:
            start_time = time.time()
            
            enhancement_prompt = f"""You are an expert agricultural translator for Indian farmers. You understand Hindi-English code-switching and farming terminology.

Original transcription (Hindi/English mixed): "{transcription}"

Please analyze and enhance this transcription by:

1. Translate to clear, proper English
2. Fix any grammatical errors or unclear references
3. Extract key agricultural terms mentioned
4. Provide confidence assessment

Respond in this exact JSON format:
{{
    "translation": "Clear English translation with proper grammar and context",
    "agricultural_terms": ["list", "of", "farming", "terms", "mentioned"],
    "confidence": "High/Medium/Low based on transcription clarity",
    "reasoning": "Brief explanation of translation decisions"
}}

Context: Indian farmers often mix Hindi and English when discussing:
- Crop diseases and pests
- Fertilizers and pesticides  
- Market prices and selling
- Planting and harvesting techniques
- Government schemes and subsidies
- Soil and weather conditions"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert agricultural translator and advisor for Indian farmers. Always respond with valid JSON."},
                    {"role": "user", "content": enhancement_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            end_time = time.time()
            content = response.choices[0].message.content.strip()
            
            logger.info(f"Enhancement time: {end_time - start_time:.2f}s")
            logger.debug(f"Raw LLM response: {content[:200]}...")
            
            # Parse JSON response
            parsed_response = self._parse_json_response(content)
            return parsed_response
            
        except Exception as e:
            logger.error(f"Enhancement error: {str(e)}")
            return None
    
    def _parse_json_response(self, content: str) -> dict:
        try:
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            if not content:
                logger.warning("Warning: Empty response from LLM")
                return None
            
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            logger.warning(f"Warning: JSON parse error - {e}")
            logger.debug(f"Content: {content}")
            
            # Try to extract JSON within the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # Fallback: create a basic response
            return {
                "translation": "LLM response parsing failed - using original transcription",
                "agricultural_terms": [],
                "confidence": "Low",
                "reasoning": f"JSON parsing failed: {str(e)}"
            }
    
    def _create_error_response(self, error_msg: str) -> dict:
        return {
            "success": False,
            "error": error_msg,
            "original_transcription": "",
            "translation": "",
            "agricultural_terms": [],
            "confidence": "Low",
            "reasoning": f"Pipeline error: {error_msg}"
        }
    
    def _create_fallback_response(self, transcription: str) -> dict:
        return {
            "success": True,
            "original_transcription": transcription,
            "translation": transcription,  # Use original as fallback
            "agricultural_terms": [],
            "confidence": "Low",
            "reasoning": "Enhancement failed, using original transcription"
        }


# TODO: Future agentic services integration
class AgenticServiceProcessor:
    """
    Placeholder for future agentic services that will process
    translation results and provide specialized agricultural responses.
    """
    
    @staticmethod
    async def process_with_agents(translation_data: dict) -> str:
        """
        Future: Route to specialized agents based on translation content
        - Disease detection agents
        - Market price agents  
        - Government scheme agents
        - Weather advisory agents
        """
        logger.info("======== Processing with Agentic Services ========")
        logger.info(f"Translation: {translation_data.get('translation', '')}")
        
        # For now, return a placeholder response
        return "This is a placeholder response. Future agentic services will process the translation and provide specialized agricultural advice."