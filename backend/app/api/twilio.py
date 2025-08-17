from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
from typing import Optional
from datetime import datetime
import os
import requests
from app.services.twilio_service import TwilioService
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/twilio",
    tags=["twilio"]
)

twilio_service = TwilioService()

# Ensure output directory exists (matching your existing structure)
os.makedirs('output', exist_ok=True)


@router.get("/")
@router.post("/")
async def hello_monkey():
    """Respond to incoming calls with a simple text message and start recording."""
    
    resp = VoiceResponse()
    resp.say("Namaste mae aap ki Krishi Saarthi! Aaj mae aap ki sahaayuh ta kae se kurr suk ti hoon?")
    
    resp.record(
        action='/api/twilio/recording-complete',
        method='POST',
        finish_on_key='#',
        play_beep=True
    )
    
    resp.say("Thank you for your message. Goodbye!")
    
    return Response(content=str(resp), media_type="application/xml")


@router.post("/voice")
async def handle_voice():
    """Alternative endpoint name for voice handling"""
    return await hello_monkey()


@router.post("/recording-complete")
async def recording_complete(
    RecordingUrl: Optional[str] = Form(None),
    RecordingSid: Optional[str] = Form(None),
    RecordingDuration: Optional[str] = Form(None),
    From: Optional[str] = Form(None)
):
    """Handle the recording completion webhook and save recording to output folder."""
    
    caller_number = From or 'unknown'
    
    print(f"Recording completed!")
    print(f"Recording SID: {RecordingSid}")
    print(f"Recording URL: {RecordingUrl}")
    print(f"Duration: {RecordingDuration} seconds")
    print(f"Caller: {caller_number}")
    try:
        if not RecordingUrl:
            print("XXXXXXXX Recording URL not available XXXXXXXX")
            return Response(content=str(VoiceResponse()), media_type="application/xml")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_caller = ''.join(c for c in caller_number if c.isalnum())
        filename = f"recording_{timestamp}_{clean_caller}_{RecordingSid}.wav"
        filepath = os.path.join('output', filename)

        wav_url = RecordingUrl + '.wav'
        
        print(f"Downloading recording from: {wav_url}")
        print(f"Saving to: {filepath}")
        
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            raise ValueError("Missing Twilio credentials for authentication")
        
        response = requests.get(
            wav_url,
            auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
            stream=True
        )
        
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Recording saved successfully to: {filepath}")
            
            if RecordingSid:
                recording = twilio_service.client.recordings(RecordingSid)
                recording.delete()
            
            if caller_number != 'unknown':
                print(f"Processing audio with ML model...")
                
                try:
                    result_message = await twilio_service.process_audio_with_model(filepath)
                    
                    print(f"Model processing complete. Result: {result_message[:100]}...")
                    
                    sms_sent = await twilio_service.send_sms_to_caller(caller_number, result_message)
                    
                    if sms_sent:
                        print(f"Complete workflow finished successfully!")
                    else:
                        print(f"XXXXXXXX Audio processed but SMS failed to send XXXXXXXX")
                        
                except Exception as model_error:
                    print(f"XXXXXXXX Error in model processing: {str(model_error)} XXXXXXXX")
                    error_message = "Sorry, we couldn't process your question right now. Please try again later or contact our support team."
                    await twilio_service.send_sms_to_caller(caller_number, error_message)
            else:
                print("XXXXXXXX Cannot send SMS - caller number unknown XXXXXXXX")
            
        else:
            print(f"XXXXXXXX Failed to download recording. Status code: {response.status_code} XXXXXXXX")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"XXXXXXXX Error downloading recording: {str(e)} XXXXXXXX")
        
        if caller_number != 'unknown':
            error_message = "Sorry, there was a technical issue processing your call. Please try again."
            await twilio_service.send_sms_to_caller(caller_number, error_message)
    
    resp = VoiceResponse()
    resp.say("Your recording has been saved and is being processed. You will receive an SMS with the response shortly. Thank you!")
    resp.hangup()
    
    return Response(content=str(resp), media_type="application/xml")


@router.post("/sms-status")
async def handle_sms_status(
    MessageSid: str = Form(),
    MessageStatus: str = Form(),
    To: str = Form(),
    ErrorCode: Optional[str] = Form(None)
):
    """Track SMS delivery status."""
    logger.info(f"📱 SMS {MessageSid} to {To}: {MessageStatus}")
    if ErrorCode:
        logger.error(f"❌ SMS Error {ErrorCode} for {MessageSid}")
    return {"status": "received"}


@router.get("/health")
@router.post("/health")
async def health():
    """Health check endpoint."""
    print("Health check received")
    return {"status": "OK"}