import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional, Union
import shutil
from app.utils.logger import get_logger
from app.schemas.chat import ChatResponse, ErrorResponse
from app.services.chat_processing_service import ChatProcessingService
from app.services.tools.vlm_tool import VLMTool
from app.services.agents.dharti_main_agent import MainAgent

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
        
        # Format for Flutter app compatibility
        flutter_response = {
            "success": result.success,
            "response": result.response.dict(exclude_none=True)
        }
        return JSONResponse(content=flutter_response)
    
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
        
        # Format for Flutter app compatibility
        flutter_response = {
            "success": result.success,
            "response": result.response.dict(exclude_none=True)
        }
        return JSONResponse(content=flutter_response)
    
    except Exception as e:
        logger.error(f"Error processing text request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")


@router.get("/test/vlm/health")
async def test_vlm_health():
    logger.info("Testing VLM health endpoint")
    
    try:
        vlm_tool = VLMTool()
        health_result = await vlm_tool.check_health()
        
        logger.info(f"VLM health check result: {health_result}")
        return JSONResponse(content=health_result)
    
    except Exception as e:
        logger.error(f"Error checking VLM health: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Health check failed: {str(e)}"
            }
        )


@router.post("/test/vlm/analyze")
async def test_vlm_analyze(
    image_file: UploadFile = File(...),
    question: str = Form(default="What do you see in this agricultural image?")
):
    logger.info(f"Testing VLM analysis - Image: {image_file.filename}, Question: {question}")
    
    if not image_file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(status_code=400, detail="Only JPG/PNG images are supported")
    
    try:
        # Save the uploaded image temporarily
        image_filename = await ChatProcessingService.save_file(image_file, "test_image")
        image_path = os.path.join("output", image_filename)
        
        # Analyze with VLM tool
        vlm_tool = VLMTool()
        analysis_result = await vlm_tool.analyze_image(image_path, question)
        
        logger.info(f"VLM analysis result: {analysis_result}")
        
        analysis_result["image_filename"] = image_filename
        
        return JSONResponse(content=analysis_result)
    
    except Exception as e:
        logger.error(f"Error in VLM analysis test: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"VLM analysis failed: {str(e)}"
            }
        )


@router.get("/test/vlm/connection")
async def test_vlm_connection():
    logger.info("Testing VLM connection")
    
    try:
        vlm_tool = VLMTool()
        connection_result = await vlm_tool.test_connection()
        
        logger.info(f"VLM connection test result: {connection_result}")
        return JSONResponse(content=connection_result)
    
    except Exception as e:
        logger.error(f"Error testing VLM connection: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Connection test failed: {str(e)}"
            }
        )


@router.post("/test/vlm/fallback")
async def test_vlm_fallback(
    image: UploadFile = File(...),
    question: str = Form(default="What do you see in this agricultural image?")
):
    logger.info(f"Testing VLM fallback mechanism - Image: {image.filename}")
    
    if not image.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(status_code=400, detail="Only JPG/PNG images are supported")
    
    try:
        # Save the uploaded image temporarily
        image_filename = await ChatProcessingService.save_file(image, "test_fallback")
        image_path = os.path.join("output", image_filename)
        
        vlm_tool = VLMTool()
        
        original_url = vlm_tool.base_url
        vlm_tool.base_url = "http://intentionally-broken-url:9999"
        
        logger.info("Intentionally breaking VLLM URL to test fallback mechanism")
        
        analysis_result = await vlm_tool.analyze_image(image_path, question)
        
        vlm_tool.base_url = original_url
        
        logger.info(f"Fallback test result: {analysis_result}")
        
        analysis_result["test_type"] = "forced_fallback"
        analysis_result["image_filename"] = image_filename
        
        return JSONResponse(content=analysis_result)
    
    except Exception as e:
        logger.error(f"Error in VLM fallback test: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"VLM fallback test failed: {str(e)}"
            }
        )


@router.post("/test/agent")
async def test_main_agent(
    text: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    logger.info(f"Testing Main Agent - Text: '{text[:50]}...', Image: {image.filename if image else 'None'}")
    
    try:
        # Handle image upload if provided
        image_path = None
        processed_files = []
        
        if image:
            if not image.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise HTTPException(status_code=400, detail="Only JPG/PNG images are supported")
            
            image_filename = await ChatProcessingService.save_file(image, "test_agent")
            image_path = os.path.join("output", image_filename)
            processed_files.append(image_filename)
        
        # Create translation result for the agent
        translation_result = {
            "success": True,
            "original_transcription": text,
            "translation": text,
            "agricultural_terms": [],
            "confidence": "High",
            "reasoning": "Direct test input"
        }
        
        # Test Main Agent
        main_agent = MainAgent()
        agent_response = await main_agent.process_query(translation_result, image_path)
        
        # Format response for testing
        result = {
            "success": True,
            "agent_response": agent_response.dict() if hasattr(agent_response, 'dict') else str(agent_response),
            "query": text,
            "image_provided": image is not None,
            "processed_files": processed_files
        }
        
        logger.info(f"Main Agent test completed successfully")
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Error in Main Agent test: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Main Agent test failed: {str(e)}"
            }
        )