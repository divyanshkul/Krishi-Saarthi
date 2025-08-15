import os
import logging
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
import shutil

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

@router.post("/upload-recording")
async def upload_recording(audio_file: UploadFile = File(...)):
    logger.info(f"Received upload request for file: {audio_file.filename}")
    
    if not audio_file.filename.lower().endswith('.wav'):
        logger.warning(f"Invalid file type: {audio_file.filename}")
        raise HTTPException(status_code=400, detail="Only WAV files are supported")
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(audio_file.filename)[1]
    new_filename = f"recording_{timestamp}{file_extension}"
    file_path = os.path.join(output_dir, new_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        logger.info(f"Successfully saved file: {new_filename}")
        return {
            "success": True,
            "filename": new_filename,
            "message": "Recording uploaded successfully"
        }
    except Exception as e:
        logger.error(f"Error saving file {audio_file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

async def _save_file(file: UploadFile, file_type: str) -> str:
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

async def _handle_audio_only(audio_filename: str) -> dict:
    logger.info(f"Executing audio-only workflow for file: {audio_filename}")
    return {
        "workflow_type": "audio_only",
        "response": "Processing audio-only request - placeholder response",
        "analysis": "Audio transcription and agricultural analysis would go here"
    }

async def _handle_audio_with_image(audio_filename: str, image_filename: str) -> dict:
    logger.info(f"Executing audio+image workflow - Audio: {audio_filename}, Image: {image_filename}")
    return {
        "workflow_type": "audio_with_image", 
        "response": "Processing audio with image - placeholder response",
        "analysis": "Combined audio transcription and image analysis for agricultural diagnosis"
    }

async def _handle_text_only(text: str) -> dict:
    logger.info(f"Executing text-only workflow for query: '{text[:50]}...'")
    return {
        "workflow_type": "text_only",
        "response": f"Processing text query: '{text}' - placeholder response",
        "analysis": "Text-based agricultural query processing would go here"
    }

async def _handle_text_with_image(text: str, image_filename: str) -> dict:
    logger.info(f"Executing text+image workflow - Text: '{text[:50]}...', Image: {image_filename}")
    return {
        "workflow_type": "text_with_image",
        "response": f"Processing text '{text}' with image - placeholder response", 
        "analysis": "Combined text query and image analysis for agricultural guidance"
    }

@router.post("/process-audio")
async def process_audio(
    audio_file: UploadFile = File(...),
    image_file: Optional[UploadFile] = File(None)
):
    logger.info(f"Processing audio request - Audio: {audio_file.filename}, Image: {image_file.filename if image_file else None}")
    
    if not audio_file.filename.lower().endswith('.wav'):
        logger.warning(f"Invalid audio file type: {audio_file.filename}")
        raise HTTPException(status_code=400, detail="Only WAV files are supported")
    
    try:
        audio_filename = await _save_file(audio_file, "audio")
        processed_files = [audio_filename]
        
        if image_file:
            if not image_file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                logger.warning(f"Invalid image file type: {image_file.filename}")
                raise HTTPException(status_code=400, detail="Only JPG/PNG images are supported")
            image_filename = await _save_file(image_file, "image")
            processed_files.append(image_filename)
            logger.info(f"Processing audio+image workflow")
            workflow_result = await _handle_audio_with_image(audio_filename, image_filename)
        else:
            logger.info(f"Processing audio-only workflow")
            workflow_result = await _handle_audio_only(audio_filename)
        
        logger.info(f"Audio processing completed successfully")
        return {
            "success": True,
            "processed_files": processed_files,
            **workflow_result
        }
    
    except Exception as e:
        logger.error(f"Error processing audio request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@router.post("/process-text")
async def process_text(
    text: str = Form(...),
    image_file: Optional[UploadFile] = File(None)
):
    logger.info(f"Processing text request - Text: '{text[:50]}...', Image: {image_file.filename if image_file else None}")
    
    try:
        processed_files = []
        
        if image_file:
            if not image_file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                logger.warning(f"Invalid image file type: {image_file.filename}")
                raise HTTPException(status_code=400, detail="Only JPG/PNG images are supported")
            image_filename = await _save_file(image_file, "image")
            processed_files.append(image_filename)
            logger.info(f"Processing text+image workflow")
            workflow_result = await _handle_text_with_image(text, image_filename)
        else:
            logger.info(f"Processing text-only workflow")
            workflow_result = await _handle_text_only(text)
        
        logger.info(f"Text processing completed successfully")
        return {
            "success": True,
            "processed_files": processed_files,
            **workflow_result
        }
    
    except Exception as e:
        logger.error(f"Error processing text request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")