import os
import shutil
from datetime import datetime
from fastapi import UploadFile
from app.utils.logger import get_logger
from app.schemas.chat import ChatResponse, WorkflowType
from app.services.demo_content_service import DemoContentService
from app.services.agents.translation_agent import TranslationAgent, AgenticServiceProcessor

logger = get_logger(__name__)


class ChatProcessingService:
    
    def __init__(self):
        self.translation_agent = TranslationAgent()
    
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
    
    @classmethod
    async def handle_audio_only(cls, audio_filename: str) -> ChatResponse:
        logger.info(f"Executing audio-only workflow for file: {audio_filename}")
        
        try:
            # Initialize translation agent
            translation_agent = TranslationAgent()
            
            # Process audio through translation pipeline
            audio_path = os.path.join("output", audio_filename)
            translation_result = await translation_agent.process_audio(audio_path)
            
            if translation_result.get("success", False):
                logger.info(f"🔄 Translation successful, processing with agentic services...")
                
                # Process with agentic services (placeholder for now)
                agentic_response = await AgenticServiceProcessor.process_with_agents(translation_result)
                
                response_content = DemoContentService.select_demo_response(WorkflowType.AUDIO_ONLY)
                # TODO: Replace demo content with agentic_response when ready
                
                logger.info(f"📝 Final response prepared for audio-only workflow")
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
            # Initialize translation agent
            translation_agent = TranslationAgent()
            
            # Process audio through translation pipeline
            audio_path = os.path.join("output", audio_filename)
            translation_result = await translation_agent.process_audio(audio_path)
            
            if translation_result.get("success", False):
                logger.info(f"🔄 Translation successful for audio+image workflow")
                logger.info(f"🖼️  Image analysis will be integrated with translation context")
                
                # Process with agentic services (placeholder for now)
                # TODO: Include image analysis in agentic processing
                agentic_response = await AgenticServiceProcessor.process_with_agents(translation_result)
                
                response_content = DemoContentService.select_demo_response(WorkflowType.AUDIO_WITH_IMAGE)
                # TODO: Replace demo content with combined audio+image agentic response
                
                logger.info(f"📝 Final response prepared for audio+image workflow")
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
        
        response_content = DemoContentService.select_demo_response(WorkflowType.TEXT_WITH_IMAGE)
        
        result = ChatResponse(
            success=True,
            workflow_type=WorkflowType.TEXT_WITH_IMAGE,
            response=response_content,
            processed_files=[image_filename]
        )
        
        logger.debug(f"Text+image workflow result: {result}")
        return result