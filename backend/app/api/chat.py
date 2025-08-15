import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

@router.post("/upload-recording")
async def upload_recording(audio_file: UploadFile = File(...)):
    if not audio_file.filename.lower().endswith('.wav'):
        raise HTTPException(status_code=400, detail="Only WAV files are supported")
    
    # Create output directory if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(audio_file.filename)[1]
    new_filename = f"recording_{timestamp}{file_extension}"
    file_path = os.path.join(output_dir, new_filename)
    
    try:
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        return {
            "success": True,
            "filename": new_filename,
            "message": "Recording uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")