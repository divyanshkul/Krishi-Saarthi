import os
import shutil
from datetime import datetime
from fastapi import UploadFile
from openai import OpenAI
from app.core.config import settings
from app.utils.logger import get_logger
from app.schemas.chat import ChatResponse, WorkflowType
from app.services.demo_content_service import DemoContentService
from app.services.agents.translation_agent import TranslationAgent, AgenticServiceProcessor
from app.services.agents.dharti_main_agent import MainAgent

logger = get_logger(__name__)


class ChatProcessingService:
    
    def __init__(self):
        self.translation_agent = TranslationAgent()
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
    
    @staticmethod
    async def save_file(file: UploadFile, file_type: str) -> str:
        logger.info(f"Saving {file_type} file: {file.filename}")
        
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        new_filename = f"{file_type}_{timestamp}{file_extension}"
        file_path = os.path.join(output_dir, new_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Successfully saved {file_type} as: {new_filename}")
        return new_filename
    
    async def translate_to_hindi(self, english_text: str) -> str:
        """Translate English response back to Hindi using GPT-4o-mini"""
        try:
            hindi_prompt = f"""Translate this agricultural advice from English to Hindi. Keep it natural and farmer-friendly. Use simple Hindi words that farmers understand.

English text: "{english_text}"

Hindi translation:"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Translate agricultural advice to Hindi. Use simple, farmer-friendly language. Be precise, no prefixes."},
                    {"role": "user", "content": hindi_prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            hindi_translation = response.choices[0].message.content.strip()
            logger.info(f"🌐 Translated response to Hindi ({len(hindi_translation)} chars)")
            return hindi_translation
            
        except Exception as e:
            logger.error(f"Hindi translation failed: {str(e)}")
            # Fallback to original English text
            return english_text
    
    @classmethod
    async def handle_audio_only(cls, audio_filename: str) -> ChatResponse:
        logger.info(f"Executing audio-only workflow for file: {audio_filename}")
        
        try:
            # Initialize services
            chat_service = cls()
            translation_agent = TranslationAgent()
            
            # Process audio through translation pipeline
            audio_path = os.path.join("output", audio_filename)
            translation_result = await translation_agent.process_audio(audio_path)
            
            if translation_result.get("success", False):
                logger.info(f"🔄 Translation successful, processing with Main Agent...")
                
                # Process with Main Agent
                main_agent = MainAgent()
                agent_response = await main_agent.process_query(translation_result, image_path=None)
                
                logger.info(f"📝 Main Agent processing complete for audio-only workflow")
                
                # Translate response back to Hindi since translation agent was used
                hindi_text = await chat_service.translate_to_hindi(agent_response.text)
                
                # Create new response with Hindi translation
                from app.schemas.chat import ResponseContent
                response_content = ResponseContent(
                    text=hindi_text,
                    website_url=agent_response.website_url,
                    website_title=agent_response.website_title
                )
            else:
                logger.warning(f"⚠️  Translation failed, using fallback demo content")
                response_content = DemoContentService.select_demo_response(WorkflowType.AUDIO_ONLY)
        
        except Exception as e:
            logger.error(f"❌ Error in audio-only workflow: {str(e)}")
            response_content = DemoContentService.select_demo_response(WorkflowType.AUDIO_ONLY)
        
        result = ChatResponse(
            success=True,
            workflow_type=WorkflowType.AUDIO_ONLY,
            response=response_content,
            processed_files=[audio_filename]
        )
        
        logger.debug(f"Audio-only workflow result: {result}")
        return result
    
    @classmethod
    async def handle_audio_with_image(cls, audio_filename: str, image_filename: str) -> ChatResponse:
        logger.info(f"Executing audio+image workflow - Audio: {audio_filename}, Image: {image_filename}")
        
        try:
            # Initialize services
            chat_service = cls()
            translation_agent = TranslationAgent()
            
            # Process audio through translation pipeline
            audio_path = os.path.join("output", audio_filename)
            translation_result = await translation_agent.process_audio(audio_path)
            
            if translation_result.get("success", False):
                logger.info(f"🔄 Translation successful for audio+image workflow")
                logger.info(f"🤖 Processing with Main Agent...")
                
                # Process with Main Agent
                main_agent = MainAgent()
                image_path = os.path.join("output", image_filename)
                agent_response = await main_agent.process_query(translation_result, image_path)
                
                logger.info(f"📝 Main Agent processing complete")
                
                # Translate response back to Hindi since translation agent was used
                hindi_text = await chat_service.translate_to_hindi(agent_response.text)
                
                # Create new response with Hindi translation
                from app.schemas.chat import ResponseContent
                response_content = ResponseContent(
                    text=hindi_text,
                    website_url=agent_response.website_url,
                    website_title=agent_response.website_title
                )
            else:
                logger.warning(f"⚠️  Translation failed, using fallback demo content")
                response_content = DemoContentService.select_demo_response(WorkflowType.AUDIO_WITH_IMAGE)
        
        except Exception as e:
            logger.error(f"❌ Error in audio+image workflow: {str(e)}")
            response_content = DemoContentService.select_demo_response(WorkflowType.AUDIO_WITH_IMAGE)
        
        result = ChatResponse(
            success=True,
            workflow_type=WorkflowType.AUDIO_WITH_IMAGE,
            response=response_content,
            processed_files=[audio_filename, image_filename]
        )
        
        logger.debug(f"Audio+image workflow result: {result}")
        return result
    
    @classmethod
    async def handle_text_only(cls, text: str) -> ChatResponse:
        logger.info(f"Executing text-only workflow for query: '{text[:50]}...'")
        
        try:
            # Create translation result for text input
            translation_result = {
                "success": True,
                "original_transcription": text,
                "translation": text,  # Assume text is already in English
                "agricultural_terms": [],
                "confidence": "High",
                "reasoning": "Direct text input"
            }
            
            # Process with Main Agent
            logger.info(f"🤖 Processing text-only with Main Agent...")
            main_agent = MainAgent()
            agent_response = await main_agent.process_query(translation_result, image_path=None)
            
            logger.info(f"📝 Main Agent processing complete for text-only workflow")
            response_content = agent_response
        
        except Exception as e:
            logger.error(f"❌ Error in text-only workflow: {str(e)}")
            response_content = DemoContentService.select_demo_response(WorkflowType.TEXT_ONLY)
        
        result = ChatResponse(
            success=True,
            workflow_type=WorkflowType.TEXT_ONLY,
            response=response_content
        )
        
        logger.debug(f"Text-only workflow result: {result}")
        return result
    
    @classmethod
    async def handle_text_with_image(cls, text: str, image_filename: str) -> ChatResponse:
        logger.info(f"Executing text+image workflow - Text: '{text[:50]}...', Image: {image_filename}")
        
        try:
            # Create translation result for text input
            translation_result = {
                "success": True,
                "original_transcription": text,
                "translation": text,  # Assume text is already in English
                "agricultural_terms": [],
                "confidence": "High",
                "reasoning": "Direct text input"
            }
            
            # Process with Main Agent
            logger.info(f"🤖 Processing text+image with Main Agent...")
            main_agent = MainAgent()
            image_path = os.path.join("output", image_filename)
            agent_response = await main_agent.process_query(translation_result, image_path)
            
            logger.info(f"📝 Main Agent processing complete")
            response_content = agent_response
        
        except Exception as e:
            logger.error(f"❌ Error in text+image workflow: {str(e)}")
            response_content = DemoContentService.select_demo_response(WorkflowType.TEXT_WITH_IMAGE)
        
        result = ChatResponse(
            success=True,
            workflow_type=WorkflowType.TEXT_WITH_IMAGE,
            response=response_content,
            processed_files=[image_filename]
        )
        
        logger.debug(f"Text+image workflow result: {result}")
        return result