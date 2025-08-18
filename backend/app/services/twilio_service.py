import os
from twilio.rest import Client
from openai import OpenAI
from app.core.config import settings
from app.services.agents.translation_agent import TranslationAgent
from app.services.agents.dharti_main_agent import MainAgent
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TwilioService:
    """Twilio service that integrates with existing TranslationAgent and MainAgent."""
    
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
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
            
            # Summarize to under 150 chars for SMS using GPT-4o-mini
            sms_response = await self.summarize_for_sms(response_text)
            logger.info(f"📱 SMS response ready: {len(sms_response)} characters")
            
            return sms_response
            
        except Exception as e:
            logger.error(f"Error in process_audio_with_model: {str(e)}")
            return "Sorry, we couldn't process your question right now. Please try again later or contact our support team."
    
    async def summarize_for_sms(self, text: str) -> str:
        """Summarize response to under 150 characters using GPT-4o-mini"""
        if len(text) <= 150:
            return text
        
        try:
            summarize_prompt = f"""Summarize this agricultural advice in under 150 characters. Be direct and actionable. No labels, no "SMS Summary:", just the advice.

Original: "{text}"

Summarized advice:"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Summarize agricultural advice precisely. Return ONLY the summarized advice, no labels or prefixes."},
                    {"role": "user", "content": summarize_prompt}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Fallback if still too long
            if len(summary) > 150:
                summary = summary[:147] + "..."
            
            return summary
            
        except Exception as e:
            logger.error(f"SMS summarization failed: {str(e)}")
            # Fallback to simple truncation
            if len(text) <= 147:
                return text
            return text[:147] + "..."
    
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