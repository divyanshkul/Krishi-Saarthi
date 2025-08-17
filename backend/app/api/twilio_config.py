from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
import requests
import os
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv
from typing import Optional
import uvicorn
import asyncio

load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Ensure recordings directory exists
os.makedirs('recordings', exist_ok=True)

app = FastAPI(title="Krishi Saarthi Voice Recording API")

async def process_audio_with_model(audio_file_path: str) -> str:
    """
    Placeholder for processing audio with a machine learning model.
    This should take the audio file path and return the processed result string.
    """
    # Simulate processing time
    await asyncio.sleep(5)
    
    # result = your_model.process(audio_file_path)
    
    # dummy response
    return "Based on your question about crop diseases, I recommend applying organic fungicide and ensuring proper drainage. For more details, visit your nearest agriculture center."


async def send_sms_to_caller(phone_number: str, message: str) -> bool:
    """Send SMS with the processed result to the caller."""
    try:
        if not TWILIO_PHONE_NUMBER:
            print("XXXXXXXX TWILIO_PHONE_NUMBER not set in environment variables XXXXXXXX")
            return False
            
        message_instance = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        print(f"SMS sent successfully to {phone_number}")
        print(f"Message SID: {message_instance.sid}")
        return True
        
    except Exception as e:
        print(f"XXXXXXXX Error sending SMS: {str(e)} XXXXXXXX")
        return False


@app.get("/")
@app.post("/")
async def hello_monkey():
    """Respond to incoming calls with a simple text message and start recording."""

    resp = VoiceResponse()
    resp.say("Namaste mae aap ki Krishi Saarthi! Aaj mae aap ki sahaayuh ta kae se kurr suk ti hoon?")
    
    # Start recording the call
    resp.record(
        action='/recording-complete',
        method='POST',
        finish_on_key='#',
        play_beep=True
    )
    
    resp.say("Thank you for your message. Goodbye!")
    
    return Response(content=str(resp), media_type="application/xml")


@app.post("/recording-complete")
async def recording_complete(
    RecordingUrl: Optional[str] = Form(None),
    RecordingSid: Optional[str] = Form(None),
    RecordingDuration: Optional[str] = Form(None),
    From: Optional[str] = Form(None)
):
    """Handle the recording completion webhook and save recording to recordings folder."""
    
    # Use 'unknown' as default for caller number
    caller_number = From or 'unknown'
    
    print(f"Recording completed!")
    print(f"Recording SID: {RecordingSid}")
    print(f"Recording URL: {RecordingUrl}")
    print(f"Duration: {RecordingDuration} seconds")
    print(f"Caller: {caller_number}")
    
    # Download and save the recording
    try:
        if not RecordingUrl:
            print("XXXXXXXX Recording URL not available XXXXXXXX")
            return Response(content=str(VoiceResponse()), media_type="application/xml")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_caller = ''.join(c for c in caller_number if c.isalnum())
        filename = f"recording_{timestamp}_{clean_caller}_{RecordingSid}.wav"
        filepath = os.path.join('recordings', filename)

        wav_url = RecordingUrl + '.wav'
        
        print(f"Downloading recording from: {wav_url}")
        print(f"Saving to: {filepath}")
        
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            raise ValueError("Missing Twilio credentials for authentication")
        
        response = requests.get(
            wav_url,
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            stream=True
        )
        
        if response.status_code == 200:
            # Save the file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Recording saved successfully to: {filepath}")
            
            if RecordingSid:
                recording = client.recordings(RecordingSid)
                recording.delete()
            
            # Process the audio with your ML model and send SMS
            if caller_number != 'unknown':
                print(f"Processing audio with ML model...")
                
                try:
                    # Process the audio file with your model
                    result_message = await process_audio_with_model(filepath)
                    
                    print(f"Model processing complete. Result: {result_message[:100]}...")
                    
                    # Send SMS with the result
                    sms_sent = await send_sms_to_caller(caller_number, result_message)
                    
                    if sms_sent:
                        print(f"Complete workflow finished successfully!")
                    else:
                        print(f"XXXXXXXX Audio processed but SMS failed to send XXXXXXXX")
                        
                except Exception as model_error:
                    print(f"XXXXXXXX Error in model processing: {str(model_error)} XXXXXXXX")
                    # Send error message to user
                    error_message = "Sorry, we couldn't process your question right now. Please try again later or contact our support team."
                    await send_sms_to_caller(caller_number, error_message)
            else:
                print("XXXXXXXX Cannot send SMS - caller number unknown XXXXXXXX")
            
        else:
            print(f"XXXXXXXX Failed to download recording. Status code: {response.status_code} XXXXXXXX")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"XXXXXXXX Error downloading recording: {str(e)} XXXXXXXX")
        
        # Send error SMS to caller if we have their number
        if caller_number != 'unknown':
            error_message = "Sorry, there was a technical issue processing your call. Please try again."
            await send_sms_to_caller(caller_number, error_message)
    
    resp = VoiceResponse()
    resp.say("Your recording has been saved and is being processed. You will receive an SMS with the response shortly. Thank you!")
    resp.hangup()
    
    return Response(content=str(resp), media_type="application/xml")


@app.get("/health")
@app.post("/health")
async def health():
    """Health check endpoint."""
    print("Health check received")
    return {"status": "OK"}


if __name__ == "__main__":
    uvicorn.run("twilio_config:app", host="0.0.0.0", port=3000, reload=True)