import os
from twilio.rest import Client
from app.core.config import settings
from app.services.agents.translation_agent import TranslationAgent
from app.services.agents.dharti_main_agent import MainAgent
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TwilioService:
    """Twilio service that integrates with existing TranslationAgent and MainAgent."""
    
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.translation_agent = TranslationAgent()
        self.main_agent = MainAgent()
    
    async def process_audio_with_model(self, audio_file_path: str) -> str:
        """Process audio with TranslationAgent and MainAgent."""
        try:
            logger.info(f"🎙️ Processing audio file: {audio_file_path}")
            
            # Process with Translation Agent (audio-only workflow)
            translation_result = await self.translation_agent.process_audio(audio_file_path)
            
            if not translation_result.get("success", False):
                logger.error("Translation failed, using fallback")
                return "Sorry, we couldn't process your question right now. Please try again later or contact our support team."
            
            # Process with Main Agent
            agent_response = await self.main_agent.process_query(translation_result, image_path=None)
            
            # Extract text response
            if hasattr(agent_response, 'text'):
                response_text = agent_response.text
            elif isinstance(agent_response, str):
                response_text = agent_response
            else:
                response_text = str(agent_response)
            
            logger.info(f"📝 Agent response generated: {len(response_text)} characters")
            
            # Truncate to 160 chars for SMS
            truncated_response = self.truncate_response(response_text)
            logger.info(f"📱 SMS response ready: {len(truncated_response)} characters")
            
            return truncated_response
            
        except Exception as e:
            logger.error(f"Error in process_audio_with_model: {str(e)}")
            return "Sorry, we couldn't process your question right now. Please try again later or contact our support team."
    
    def truncate_response(self, text: str, max_chars: int = 160) -> str:
        """Truncate response to SMS-friendly length"""
        if len(text) <= max_chars:
            return text
        
        # Smart truncation at word boundary if possible
        if ' ' in text[:max_chars-3]:
            truncated = text[:max_chars-3].rsplit(' ', 1)[0]
            return truncated + "..."
        else:
            return text[:157] + "..."
    
    async def send_sms_to_caller(self, phone_number: str, message: str) -> bool:
        """Send SMS with the processed result to the caller."""
        try:
            if not settings.TWILIO_PHONE_NUMBER:
                print("XXXXXXXX TWILIO_PHONE_NUMBER not set in environment variables XXXXXXXX")
                return False
                
            message_instance = self.client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            print(f"SMS sent successfully to {phone_number}")
            print(f"Message SID: {message_instance.sid}")
            return True
            
        except Exception as e:
            print(f"XXXXXXXX Error sending SMS: {str(e)} XXXXXXXX")
            return False