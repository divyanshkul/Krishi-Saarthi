import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional, Union
import shutil
from app.utils.logger import get_logger
from app.schemas.chat import ChatResponse, ErrorResponse
from app.services.chat_processing_service import ChatProcessingService

logger = get_logger(__name__)

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
        response = {
            "success": True,
            "filename": new_filename,
            "message": "Recording uploaded successfully"
        }
        logger.debug(f"Returning response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error saving file {audio_file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")


@router.post("/process-audio", response_model=Union[ChatResponse, ErrorResponse])
async def process_audio(
    audio_file: UploadFile = File(...),
    image_file: Optional[UploadFile] = File(None)
):
    logger.info(f"Processing audio request - Audio: {audio_file.filename}, Image: {image_file.filename if image_file else None}")
    
    if not audio_file.filename.lower().endswith('.wav'):
        logger.warning(f"Invalid audio file type: {audio_file.filename}")
        raise HTTPException(status_code=400, detail="Only WAV files are supported")
    
    try:
        audio_filename = await ChatProcessingService.save_file(audio_file, "audio")
        
        if image_file:
            if not image_file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                logger.warning(f"Invalid image file type: {image_file.filename}")
                raise HTTPException(status_code=400, detail="Only JPG/PNG images are supported")
            image_filename = await ChatProcessingService.save_file(image_file, "image")
            logger.info(f"Processing audio+image workflow")
            result = await ChatProcessingService.handle_audio_with_image(audio_filename, image_filename)
        else:
            logger.info(f"Processing audio-only workflow")
            result = await ChatProcessingService.handle_audio_only(audio_filename)
        
        logger.info(f"Audio processing completed successfully")
        return JSONResponse(content=result.dict(exclude_none=True))
    
    except Exception as e:
        logger.error(f"Error processing audio request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")


@router.post("/process-text", response_model=Union[ChatResponse, ErrorResponse])
async def process_text(
    text: str = Form(...),
    image_file: Optional[UploadFile] = File(None)
):
    logger.info(f"Processing text request - Text: '{text[:50]}...', Image: {image_file.filename if image_file else None}")
    
    try:
        if image_file:
            if not image_file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                logger.warning(f"Invalid image file type: {image_file.filename}")
                raise HTTPException(status_code=400, detail="Only JPG/PNG images are supported")
            image_filename = await ChatProcessingService.save_file(image_file, "image")
            logger.info(f"Processing text+image workflow")
            result = await ChatProcessingService.handle_text_with_image(text, image_filename)
        else:
            logger.info(f"Processing text-only workflow")
            result = await ChatProcessingService.handle_text_only(text)
        
        logger.info(f"Text processing completed successfully")
        return JSONResponse(content=result.dict(exclude_none=True))
    
    except Exception as e:
        logger.error(f"Error processing text request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")